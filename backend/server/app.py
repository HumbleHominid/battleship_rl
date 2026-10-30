import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from game.agents import AGENT_REGISTRY
from server.ws_session import FastAPIWebSocketAdapter
from game.game_engine import GameEngine


# ------------------------------------------------------------------
# App lifecycle
# ------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.WARNING)
    yield
    for record in list(_games.values()):
        await _cancel(record)


app = FastAPI(title="Battleship RL Server", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# In-memory game store
# ------------------------------------------------------------------

@dataclass
class GameRecord:
    game_id: str
    engine: GameEngine
    adapter: FastAPIWebSocketAdapter
    task: asyncio.Task
    agent: str
    player_placement: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def status(self) -> str:
        if self.task.done() or self.engine.game_over:
            return "finished"
        return "active"


_games: dict[str, GameRecord] = {}


# ------------------------------------------------------------------
# Request / response models
# ------------------------------------------------------------------

class CreateGameRequest(BaseModel):
    agent: str = Field(default="q-agent", description="Agent key: random, hunt, bayes, q-agent")
    player_placement: str = Field(default="random", pattern="^(random|manual)$")


class CreateGameResponse(BaseModel):
    game_id: str
    ws_url: str
    agent: str
    player_placement: str


class GameStatusResponse(BaseModel):
    game_id: str
    status: str
    agent: str
    player_placement: str
    created_at: str
    turn: int
    game_over: bool
    winner: Optional[str]
    player_score: dict
    agent_score: dict


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

async def _cancel(record: GameRecord) -> None:
    if not record.task.done():
        record.task.cancel()
        try:
            await record.task
        except (asyncio.CancelledError, Exception):
            pass


def _record_to_status(r: GameRecord) -> GameStatusResponse:
    return GameStatusResponse(
        game_id=r.game_id,
        status=r.status,
        agent=r.agent,
        player_placement=r.player_placement,
        created_at=r.created_at.isoformat(),
        turn=r.engine.turn,
        game_over=r.engine.game_over,
        winner=r.engine.winner,
        player_score=r.engine.player_score,
        agent_score=r.engine.agent_score,
    )


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------

@app.post("/games", response_model=CreateGameResponse, status_code=201)
async def create_game(req: CreateGameRequest, request: Request):
    if req.agent not in AGENT_REGISTRY:
        raise HTTPException(400, f"Unknown agent '{req.agent}'. Valid: {list(AGENT_REGISTRY)}")

    adapter = FastAPIWebSocketAdapter()
    engine = GameEngine(
        agent=AGENT_REGISTRY[req.agent](),
        ws_server=adapter,
        player_placement=req.player_placement,
        headless=True,
    )
    task = asyncio.create_task(engine.run(), name=f"game-{adapter.game_id}")

    _games[adapter.game_id] = GameRecord(
        game_id=adapter.game_id,
        engine=engine,
        adapter=adapter,
        task=task,
        agent=req.agent,
        player_placement=req.player_placement,
    )

    base = str(request.base_url).rstrip("/").replace("http://", "ws://").replace("https://", "wss://")
    ws_url = f"{base}/games/{adapter.game_id}/ws"

    return CreateGameResponse(
        game_id=adapter.game_id,
        ws_url=ws_url,
        agent=req.agent,
        player_placement=req.player_placement,
    )


@app.get("/games", response_model=list[GameStatusResponse])
async def list_games():
    return [_record_to_status(r) for r in _games.values()]


@app.get("/games/{game_id}", response_model=GameStatusResponse)
async def get_game(game_id: str):
    record = _games.get(game_id)
    if not record:
        raise HTTPException(404, "Game not found")
    return _record_to_status(record)


@app.delete("/games/{game_id}", status_code=204)
async def delete_game(game_id: str):
    record = _games.pop(game_id, None)
    if not record:
        raise HTTPException(404, "Game not found")
    await _cancel(record)


@app.websocket("/games/{game_id}/ws")
async def game_ws(game_id: str, websocket: WebSocket):
    record = _games.get(game_id)
    if not record:
        await websocket.close(code=4004)
        return
    if record.status == "finished":
        await websocket.close(code=4000)
        return
    await record.adapter.connect(websocket)
