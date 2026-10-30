"""End-to-end checks: python -m pytest test_game.py"""

import asyncio
import json

from fastapi.testclient import TestClient

from game.agents import BayesianAgent, HuntAgent, QAgent, RandomAgent
from game.game_engine import GameEngine
from server import app


def _play(agent, player_agent) -> GameEngine:
    engine = GameEngine(agent=agent, player_agent=player_agent, headless=True)
    asyncio.run(engine.run())
    return engine


def test_every_agent_finishes_a_game():
    for agent in (RandomAgent(), HuntAgent(), BayesianAgent(), QAgent()):
        engine = _play(agent, RandomAgent())
        assert engine.game_over
        loser = engine.player_board if engine.winner == "agent" else engine.agent_board
        assert loser.all_ships_sunk()


def _unshot_cells(view: dict) -> list[str]:
    return [
        f"{'ABCDEFGHIJ'[r]}{c + 1}"
        for r, row in enumerate(view["enemy_board"])
        for c, cell in enumerate(row)
        if cell.endswith(":EMPTY")
    ]


def test_ws_player_plays_a_full_game():
    with TestClient(app) as client:
        created = client.post("/games", json={"agent": "random"}).json()
        game_id = created["game_id"]

        with client.websocket_connect(f"/games/{game_id}/ws") as ws:
            ws.send_text(json.dumps({"type": "hello", "role": "player"}))
            assert json.loads(ws.receive_text())["type"] == "welcome"

            seen = set()
            while True:
                msg = json.loads(ws.receive_text())
                seen.add(msg["type"])
                if msg["type"] == "player_view":
                    # Fog of war: no unhit agent ship may be visible.
                    assert all(
                        cell.startswith("NONE:") or cell.endswith(":HIT")
                        for row in msg["enemy_board"]
                        for cell in row
                    )
                    move = {"type": "move", "coordinate": _unshot_cells(msg)[0]}
                    ws.send_text(json.dumps(move))
                elif msg["type"] == "game_over":
                    break

        assert {"game_start", "player_view", "move_ack", "game_state"} <= seen
        status = client.get(f"/games/{game_id}").json()
        assert status["status"] == "finished"
        assert status["winner"] in ("player", "agent")
