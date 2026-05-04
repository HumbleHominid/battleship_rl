import argparse
import asyncio
import logging
import time
import zipfile

from game.agents import AGENT_REGISTRY
from game.game_engine import GameEngine
from game.logger import GameLogger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Battleship RL — play Battleship against an RL agent"
    )
    parser.add_argument(
        "--agent",
        default="random",
        help="Agent key from AGENT_REGISTRY (default: random)",
    )
    parser.add_argument(
        "--player-type",
        choices=["random", "websocket"],
        default="random",
        help="Player type: 'random' stub or 'websocket' human (default: random)",
    )
    parser.add_argument(
        "--player-placement",
        choices=["random", "manual"],
        default="random",
        help="Fleet placement for WS player: 'random' or 'manual' via WS protocol (default: random)",
    )
    parser.add_argument(
        "--ws-host",
        default="localhost",
        help="WebSocket server hostname (default: localhost)",
    )
    parser.add_argument(
        "--ws-port",
        type=int,
        default=8765,
        help="WebSocket server port (default: 8765)",
    )
    parser.add_argument(
        "--no-ws",
        action="store_true",
        help="Disable the WebSocket server (pure terminal play)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="WARNING",
        help="Logging verbosity (default: WARNING)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without any graphical output (for testing or server environments)",
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
        help="Log the game boards to the log file (like terminal output in gui mode)",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    GameLogger.setup(getattr(logging, args.log_level))

    agent_cls = AGENT_REGISTRY.get(args.agent)
    if agent_cls is None:
        import sys

        print(
            f"error: Unknown agent '{args.agent}'. Available: {list(AGENT_REGISTRY)}",
            file=sys.stderr,
        )
        sys.exit(2)

    engine = GameEngine(
        agent=agent_cls(),
        player_type=args.player_type,
        player_placement=args.player_placement,
        ws_host=args.ws_host,
        ws_port=args.ws_port,
        enable_ws=not args.no_ws,
        headless=args.headless,
        log_boards=args.log_boards,
    )
    game_num = 1
    max_games = args.max_games
    win_dist = {"player": 0, "agent": 0}
    turns = []

    begin = time.time()
    while game_num <= max_games:
        start_text = f"GAME START — {game_num}"
        print(start_text)
        GameLogger.info(start_text)
        await engine.run()

        if engine.game_over and engine.winner:
            win_dist.update({engine.winner: win_dist[engine.winner] + 1})
            turns.append(engine.player_board.cells_targeted())

        engine.reset()
        game_num += 1

    elapsed = time.time() - begin
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)

    total_turns = sum(turns)
    avg_turns = total_turns / len(turns)
    std_turns = (sum((t - avg_turns) ** 2 for t in turns) / len(turns)) ** 0.5

    def construct_str(label: str, arg_value: str) -> str:
        prefix = f"  {label.capitalize()} ({arg_value}):"
        return f"{prefix:25s} {str(win_dist[label]):3s} wins"

    player_str = construct_str("player", args.player_type)
    agent_str = construct_str("agent", args.agent)

    print(f"Final win distribution after {max_games} games:")
    print(player_str)
    print(agent_str)
    print(f"Total elapsed time:  {hours:.0f}h {minutes:.0f}m {seconds:.2f}s")
    print(f"Average Agent turns: {avg_turns:.2f} ± {std_turns:.2f}")

    GameLogger.close()
    if GameLogger.log_file and GameLogger.log_file.exists():
        zip_path = GameLogger.log_file.with_suffix(".zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(GameLogger.log_file, GameLogger.log_file.name)
        GameLogger.log_file.unlink()
        print(f"\nLog archived to {zip_path}")


if __name__ == "__main__":
    asyncio.run(main())
