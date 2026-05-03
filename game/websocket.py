import asyncio
import json
import uuid
from typing import Optional

import websockets
from websockets.server import WebSocketServerProtocol  # type: ignore

from .logger import GameLogger


class GameWebSocketServer:
    """
    Embedded WebSocket server that:
      - Broadcasts game state to all connected observers after every move.
      - Accepts a single player connection; receives move and placement commands
        from it and puts them on asyncio queues for the game loop to consume.

    Connection protocol:
      Client sends first: {"type": "hello", "role": "observer"}  or  "player"
      Server replies:     {"type": "welcome", "game_id": "...", "role": "..."}

    Only one player is accepted at a time; subsequent "player" connections
    are downgraded to observers.
    """

    def __init__(self, host: str = "localhost", port: int = 8765) -> None:
        self.host = host
        self.port = port
        self.game_id: str = str(uuid.uuid4())
        self._observers: set[WebSocketServerProtocol] = set()
        self._player_ws: Optional[WebSocketServerProtocol] = None
        self._player_move_queue: asyncio.Queue[str] = asyncio.Queue()
        self._player_placement_queue: asyncio.Queue[dict] = asyncio.Queue()
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
            GameLogger.info(
                "WebSocket server listening on ws://%s:%d", self.host, self.port
            )
            try:
                await asyncio.Future()  # run forever until cancelled
            except asyncio.CancelledError:
                pass
        self._server = None
        GameLogger.info("WebSocket server stopped")

    async def stop(self) -> None:
        """Send close frames to all connected clients."""
        all_clients = set(self._observers)
        if self._player_ws:
            all_clients.add(self._player_ws)
        if all_clients:
            await asyncio.gather(
                *(ws.close() for ws in all_clients), return_exceptions=True
            )
        self._observers.clear()
        self._player_ws = None

    # ------------------------------------------------------------------
    # Connection handler
    # ------------------------------------------------------------------

    async def _handler(self, websocket: WebSocketServerProtocol) -> None:
        """Entry point for each new connection. Reads role, routes accordingly."""
        try:
            raw = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            msg = json.loads(raw)
        except (asyncio.TimeoutError, json.JSONDecodeError, Exception) as e:
            GameLogger.warn("Bad handshake from %s: %s", websocket.remote_address, e)
            await websocket.close()
            return

        role = msg.get("role", "observer")

        if role == "player" and self._player_ws is None:
            actual_role = "player"
        else:
            if role in ("player", "rl_agent"):
                GameLogger.warn(
                    "Downgrading %s connection from %s to observer",
                    websocket.remote_address,
                    role,
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

        if actual_role == "player":
            await self._handle_player(websocket)
        else:
            await self._handle_observer(websocket)

    async def _handle_player(self, websocket: WebSocketServerProtocol) -> None:
        """Receive move and placement commands from the player and enqueue them."""
        self._player_ws = websocket
        GameLogger.info("Player connected from %s", websocket.remote_address)
        try:
            async for raw in websocket:
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    GameLogger.warn("Player sent non-JSON: %s", raw)
                    continue
                if msg.get("type") == "move":
                    coord = msg.get("coordinate", "")
                    if coord:
                        await self._player_move_queue.put(coord)
                    else:
                        GameLogger.warn("Player move missing 'coordinate' field")
                elif msg.get("type") == "placement":
                    await self._player_placement_queue.put(msg)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self._player_ws = None
            GameLogger.info("Player disconnected")

    async def _handle_observer(self, websocket: WebSocketServerProtocol) -> None:
        """Register an observer and hold its connection open until disconnect."""
        self._observers.add(websocket)
        GameLogger.info(
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
            GameLogger.info(
                "Observer disconnected (remaining: %d)", len(self._observers)
            )

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

    async def send_to_player(self, message_dict: dict) -> None:
        """Send a JSON message to the connected player. No-op if none connected."""
        if self._player_ws is None:
            return
        try:
            await self._player_ws.send(json.dumps(message_dict))
        except websockets.exceptions.ConnectionClosed:
            self._player_ws = None

    async def wait_for_player_move(self) -> str:
        """Await the next move coordinate from the player's move queue."""
        return await self._player_move_queue.get()

    async def wait_for_player_placement(self) -> dict:
        """Await the next ship placement message from the player's placement queue."""
        return await self._player_placement_queue.get()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def player_connected(self) -> bool:
        return self._player_ws is not None
