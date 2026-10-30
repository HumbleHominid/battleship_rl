import argparse
import asyncio
import logging
import statistics
import time
import zipfile

from app_logger import setup_logging
from game.agents import AGENT_REGISTRY, BaseAgent, QAgent
from game.game_engine import GameEngine

log = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Battleship RL — evaluate agents against each other"
    )
    parser.add_argument(
        "--agent",
        choices=list(AGENT_REGISTRY),
        default="random",
        help="Agent under evaluation (default: random)",
    )
    parser.add_argument(
        "--player-type",
        choices=list(AGENT_REGISTRY),
        default="random",
        help="Opposing agent (default: random)",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="checkpoints/q_agent.pt",
        help="Checkpoint file for the q-agent",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging verbosity (default: INFO)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Suppress per-turn board display",
    )
    parser.add_argument(
        "--max-games",
        type=int,
        default=100,
        help="Number of games to play before exiting (default: 100)",
    )
    parser.add_argument(
        "--log-boards",
        action="store_true",
        help="Log the game boards to the log file instead of printing them",
    )
    return parser.parse_args()


def _make_agent(name: str, checkpoint: str) -> BaseAgent:
    agent_cls = AGENT_REGISTRY[name]
    return agent_cls(checkpoint) if agent_cls is QAgent else agent_cls()


async def run_game() -> None:
    args = parse_args()
    log_file = setup_logging("game", args.log_level)

    engine = GameEngine(
        agent=_make_agent(args.agent, args.checkpoint),
        player_agent=_make_agent(args.player_type, args.checkpoint),
        headless=args.headless,
        log_boards=args.log_boards,
    )
    win_dist = {"player": 0, "agent": 0}
    turns = []

    begin = time.time()
    for game_num in range(1, args.max_games + 1):
        log.info(f"GAME START — {game_num}")
        await engine.run()

        win_dist[engine.winner] += 1
        turns.append(engine.player_board.cells_targeted())

        engine.reset()

    elapsed = time.time() - begin
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)

    def construct_str(label: str, arg_value: str) -> str:
        prefix = f"  {label.capitalize()} ({arg_value}):"
        return f"{prefix:25s} {str(win_dist[label]):3s} wins"

    print(f"Final win distribution after {args.max_games} games:")
    print(construct_str("player", args.player_type))
    print(construct_str("agent", args.agent))
    print(f"Total elapsed time:  {hours:.0f}h {minutes:.0f}m {seconds:.2f}s")
    print(
        f"Average Agent turns: {statistics.fmean(turns):.2f} ± {statistics.pstdev(turns):.2f}"
    )

    logging.shutdown()
    zip_path = log_file.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(log_file, log_file.name)
    log_file.unlink()
    print(f"\nLog archived to {zip_path}")


if __name__ == "__main__":
    asyncio.run(run_game())
