import asyncio
import json
import uuid
from typing import Optional

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from .game_logger import GameLogger


class FastAPIWebSocketAdapter:
    """
    Drop-in replacement for GameWebSocketServer that accepts FastAPI/Starlette
    WebSocket objects instead of raw websockets.WebSocketServerProtocol objects.

    GameEngine calls the same interface it uses on GameWebSocketServer:
      start(), stop(), broadcast_state(), send_to_player(),
      wait_for_player_move(), wait_for_player_placement(), player_connected, game_id

    The FastAPI WS endpoint calls connect(websocket) for each new client.
    """

    def __init__(self, game_id: str | None = None) -> None:
        self.game_id: str = game_id or str(uuid.uuid4())
        self._observers: list[WebSocket] = []
        self._player_ws: Optional[WebSocket] = None
        self._player_move_queue: asyncio.Queue[str] = asyncio.Queue()
        self._player_placement_queue: asyncio.Queue[dict] = asyncio.Queue()

    # ------------------------------------------------------------------
    # GameEngine lifecycle interface
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Called by GameEngine as asyncio.create_task(adapter.start()).
        Suspends until cancelled — no actual server to start."""
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            pass

    async def stop(self) -> None:
        """Called by GameEngine in its finally block. Closes all open connections."""
        targets: list[WebSocket] = list(self._observers)
        if self._player_ws is not None:
            targets.append(self._player_ws)
        await asyncio.gather(*(ws.close() for ws in targets), return_exceptions=True)
        self._observers.clear()
        self._player_ws = None

    # ------------------------------------------------------------------
    # FastAPI WS endpoint entry point
    # ------------------------------------------------------------------

    async def connect(self, websocket: WebSocket) -> None:
        """Called by the FastAPI WS endpoint for every new connection.
        Performs the hello/welcome handshake then routes to player or observer loop."""
        await websocket.accept()

        try:
            raw = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
            msg = json.loads(raw)
        except (asyncio.TimeoutError, json.JSONDecodeError, Exception) as e:
            GameLogger.warn("Bad WS handshake: %s", e)
            await websocket.close()
            return

        role = msg.get("role", "observer")

        if role == "player" and self._player_ws is None:
            actual_role = "player"
        else:
            if role == "player":
                GameLogger.warn(
                    "Second player connection downgraded to observer (game_id=%s)",
                    self.game_id,
                )
            actual_role = "observer"

        await websocket.send_text(
            json.dumps({"type": "welcome", "game_id": self.game_id, "role": actual_role})
        )

        if actual_role == "player":
            await self._handle_player(websocket)
        else:
            await self._handle_observer(websocket)

    async def _handle_player(self, websocket: WebSocket) -> None:
        self._player_ws = websocket
        GameLogger.info("WS player connected (game_id=%s)", self.game_id)
        try:
            while True:
                try:
                    raw = await websocket.receive_text()
                except WebSocketDisconnect:
                    break
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
        finally:
            self._player_ws = None
            GameLogger.info("WS player disconnected (game_id=%s)", self.game_id)

    async def _handle_observer(self, websocket: WebSocket) -> None:
        self._observers.append(websocket)
        GameLogger.info(
            "WS observer connected (game_id=%s, total=%d)",
            self.game_id,
            len(self._observers),
        )
        try:
            while True:
                try:
                    await websocket.receive_text()
                except WebSocketDisconnect:
                    break
        finally:
            if websocket in self._observers:
                self._observers.remove(websocket)
            GameLogger.info(
                "WS observer disconnected (game_id=%s, remaining=%d)",
                self.game_id,
                len(self._observers),
            )

    # ------------------------------------------------------------------
    # GameEngine messaging interface
    # ------------------------------------------------------------------

    async def broadcast_state(self, state_dict: dict) -> None:
        if not self._observers:
            return
        payload = json.dumps(state_dict)
        dead: list[WebSocket] = []
        for ws in list(self._observers):
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            if ws in self._observers:
                self._observers.remove(ws)

    async def send_to_player(self, message_dict: dict) -> None:
        if self._player_ws is None:
            return
        try:
            await self._player_ws.send_text(json.dumps(message_dict))
        except Exception:
            self._player_ws = None

    async def wait_for_player_move(self) -> str:
        return await self._player_move_queue.get()

    async def wait_for_player_placement(self) -> dict:
        return await self._player_placement_queue.get()

    @property
    def player_connected(self) -> bool:
        return self._player_ws is not None
