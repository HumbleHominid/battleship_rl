import argparse
import asyncio
import logging

from game.game_engine import GameEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Battleship RL — play Battleship against an RL agent"
    )
    parser.add_argument(
        "--mode",
        choices=["automated", "interactive"],
        default="automated",
        help="Game mode: 'automated' runs without user input (default); "
        "'interactive' lets the user place ships and make moves",
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
    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s %(name)s: %(message)s",
    )

    engine = GameEngine(
        mode=args.mode,
        ws_host=args.ws_host,
        ws_port=args.ws_port,
        enable_ws=not args.no_ws,
    )
    await engine.run()


if __name__ == "__main__":
    asyncio.run(main())
