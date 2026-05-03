import argparse
import asyncio
import logging

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
    )
    await engine.run()


if __name__ == "__main__":
    asyncio.run(main())
