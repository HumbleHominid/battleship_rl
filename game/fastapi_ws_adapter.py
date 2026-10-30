import asyncio
import json
import logging
import uuid
from typing import Optional

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

log = logging.getLogger(__name__)


class FastAPIWebSocketAdapter:
    """
    Connects a single WebSocket player to a GameEngine.

    The FastAPI WS endpoint calls connect(websocket); GameEngine calls the rest.
    """

    def __init__(self) -> None:
        self.game_id: str = str(uuid.uuid4())
        self._player_ws: Optional[WebSocket] = None
        self._player_move_queue: asyncio.Queue[str] = asyncio.Queue()
        self._player_placement_queue: asyncio.Queue[dict] = asyncio.Queue()

    async def stop(self) -> None:
        """Called by GameEngine in its finally block. Closes the player connection."""
        if self._player_ws is not None:
            try:
                await self._player_ws.close()
            except Exception:
                pass
        self._player_ws = None

    # ------------------------------------------------------------------
    # FastAPI WS endpoint entry point
    # ------------------------------------------------------------------

    async def connect(self, websocket: WebSocket) -> None:
        """Perform the hello/welcome handshake, then read player messages until disconnect."""
        await websocket.accept()

        try:
            raw = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
            msg = json.loads(raw)
        except Exception as e:
            log.warning("Bad WS handshake: %s", e)
            await websocket.close()
            return

        if msg.get("role") != "player" or self._player_ws is not None:
            log.warning("Rejected WS connection (game_id=%s)", self.game_id)
            await websocket.close(code=4003)
            return

        await websocket.send_text(
            json.dumps({"type": "welcome", "game_id": self.game_id, "role": "player"})
        )
        await self._handle_player(websocket)

    async def _handle_player(self, websocket: WebSocket) -> None:
        self._player_ws = websocket
        log.info("WS player connected (game_id=%s)", self.game_id)
        try:
            while True:
                try:
                    raw = await websocket.receive_text()
                except WebSocketDisconnect:
                    break
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    log.warning("Player sent non-JSON: %s", raw)
                    continue
                if msg.get("type") == "move":
                    coord = msg.get("coordinate", "")
                    if coord:
                        await self._player_move_queue.put(coord)
                    else:
                        log.warning("Player move missing 'coordinate' field")
                elif msg.get("type") == "placement":
                    await self._player_placement_queue.put(msg)
        finally:
            self._player_ws = None
            log.info("WS player disconnected (game_id=%s)", self.game_id)

    # ------------------------------------------------------------------
    # GameEngine messaging interface
    # ------------------------------------------------------------------

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
