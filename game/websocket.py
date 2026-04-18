import asyncio
import json
import logging
import uuid
from typing import Optional

import websockets
from websockets.server import WebSocketServerProtocol  # type: ignore

logger = logging.getLogger(__name__)


class GameWebSocketServer:
    """
    Embedded WebSocket server that:
      - Broadcasts game state to all connected observers after every move.
      - Accepts a single RL agent connection; receives move commands from it
        and puts them on an asyncio queue for the game loop to consume.

    Connection protocol:
      Client sends first: {"type": "hello", "role": "observer"}  or  "rl_agent"
      Server replies:     {"type": "welcome", "game_id": "...", "role": "..."}

    Only one rl_agent is accepted at a time; subsequent "rl_agent" connections
    are downgraded to observers.
    """

    def __init__(self, host: str = "localhost", port: int = 8765) -> None:
        self.host = host
        self.port = port
        self.game_id: str = str(uuid.uuid4())
        self._observers: set[WebSocketServerProtocol] = set()
        self._agent_ws: Optional[WebSocketServerProtocol] = None
        self._move_queue: asyncio.Queue[str] = asyncio.Queue()
        self._server = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """
        Launch the WebSocket server and keep it alive until this coroutine is cancelled.
        Intended to be run as an asyncio.create_task().
        """
        async with websockets.serve(self._handler, self.host, self.port) as server:
            self._server = server
            logger.info(
                "WebSocket server listening on ws://%s:%d", self.host, self.port
            )
            try:
                await asyncio.Future()  # run forever until cancelled
            except asyncio.CancelledError:
                pass
        self._server = None
        logger.info("WebSocket server stopped")

    async def stop(self) -> None:
        """Send close frames to all connected clients."""
        all_clients = set(self._observers)
        if self._agent_ws:
            all_clients.add(self._agent_ws)
        if all_clients:
            await asyncio.gather(
                *(ws.close() for ws in all_clients), return_exceptions=True
            )
        self._observers.clear()
        self._agent_ws = None

    # ------------------------------------------------------------------
    # Connection handler
    # ------------------------------------------------------------------

    async def _handler(self, websocket: WebSocketServerProtocol) -> None:
        """Entry point for each new connection. Reads role, routes accordingly."""
        try:
            raw = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            msg = json.loads(raw)
        except (asyncio.TimeoutError, json.JSONDecodeError, Exception) as e:
            logger.warning("Bad handshake from %s: %s", websocket.remote_address, e)
            await websocket.close()
            return

        role = msg.get("role", "observer")

        if role == "rl_agent" and self._agent_ws is None:
            actual_role = "rl_agent"
        else:
            if role == "rl_agent":
                logger.warning(
                    "Second rl_agent connection from %s; treating as observer",
                    websocket.remote_address,
                )
            actual_role = "observer"

        await websocket.send(
            json.dumps(
                {
                    "type": "welcome",
                    "game_id": self.game_id,
                    "role": actual_role,
                }
            )
        )

        if actual_role == "rl_agent":
            await self._handle_agent(websocket)
        else:
            await self._handle_observer(websocket)

    async def _handle_agent(self, websocket: WebSocketServerProtocol) -> None:
        """Receive move commands from the RL agent and enqueue them."""
        self._agent_ws = websocket
        logger.info("RL agent connected from %s", websocket.remote_address)
        try:
            async for raw in websocket:
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    logger.warning("Agent sent non-JSON: %s", raw)
                    continue
                if msg.get("type") == "move":
                    coord = msg.get("coordinate", "")
                    if coord:
                        await self._move_queue.put(coord)
                    else:
                        logger.warning("Agent move missing 'coordinate' field")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self._agent_ws = None
            logger.info("RL agent disconnected")

    async def _handle_observer(self, websocket: WebSocketServerProtocol) -> None:
        """Register an observer and hold its connection open until disconnect."""
        self._observers.add(websocket)
        logger.info(
            "Observer connected from %s (total: %d)",
            websocket.remote_address,
            len(self._observers),
        )
        try:
            async for _ in websocket:
                pass  # observers don't send commands
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self._observers.discard(websocket)
            logger.info("Observer disconnected (remaining: %d)", len(self._observers))

    # ------------------------------------------------------------------
    # Messaging
    # ------------------------------------------------------------------

    async def broadcast_state(self, state_dict: dict) -> None:
        """Serialize state_dict to JSON and send to all connected observers."""
        if not self._observers:
            return
        payload = json.dumps(state_dict)
        disconnected: set[WebSocketServerProtocol] = set()
        for ws in list(self._observers):
            try:
                await ws.send(payload)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(ws)
        self._observers -= disconnected

    async def send_to_agent(self, message_dict: dict) -> None:
        """Send a JSON message to the connected RL agent. No-op if none connected."""
        if self._agent_ws is None:
            return
        try:
            await self._agent_ws.send(json.dumps(message_dict))
        except websockets.exceptions.ConnectionClosed:
            self._agent_ws = None

    async def wait_for_agent_move(self) -> str:
        """
        Await the next move coordinate from the RL agent's move queue.
        The game loop calls this during the agent's turn; it yields control to
        the event loop until the agent sends a move over WebSocket.
        Returns a coordinate string like 'B5'.
        """
        return await self._move_queue.get()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def agent_connected(self) -> bool:
        return self._agent_ws is not None
