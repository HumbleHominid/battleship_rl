import argparse
import asyncio
import concurrent.futures
import inspect
import logging
import sys
import time
import zipfile

from game.agents import AGENT_REGISTRY
from game.fleet_placement_methods import PLACEMENT_METHODS
from game.game_engine import GameEngine
from game.game_logger import GameLogger
from game.models import Board, Ship, ShipType


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
        default="random",
        help="Agent key from AGENT_REGISTRY, 'websocket', or 'terminal' (default: random)",
    )
    parser.add_argument(
        "--player-placement",
        choices=["random", "manual"],
        default="random",
        help="Fleet placement for human players: 'random' (server places) or 'manual' (interactive). Applies to websocket and terminal player types (default: random)",
    )
    parser.add_argument(
        "--player-placement-method",
        choices=list(PLACEMENT_METHODS.keys()),
        default=None,
        help="Force a specific fleet placement algorithm for the player (default: weighted random). "
        f"Choices: {', '.join(PLACEMENT_METHODS.keys())}",
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
        help="Disable WebSocket server (agent-vs-agent only)",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="checkpoints/q_agent.pt",
        help="Path to a checkpoint file for agents that support it (e.g. q_learning)",
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
    parser.add_argument(
        "--board-size",
        type=int,
        default=10,
        help="Size of the game board (default: 10)",
    )
    parser.add_argument(
        "--fleet-config",
        nargs="+",
        default=[
            ShipType.CARRIER.name,
            ShipType.BATTLESHIP.name,
            ShipType.DESTROYER.name,
            ShipType.SUBMARINE.name,
            ShipType.PATROL_BOAT.name,
        ],
        help="List of ship types to include in the fleet (default: all standard ships) e.g. --fleet-config CARRIER BATTLESHIP",
    )
    parser.add_argument(
        "--report-games",
        action="store_true",
        help="Report game results (default: False)",
        default=False,
    )
    return parser.parse_args()


def _init_global_state(
    board_size: int = 10,
    fleet_config: list[ShipType] | None = None,
) -> None:
    Board.board_size = board_size
    if fleet_config is None:
        fleet_config = [s for s in ShipType if s != ShipType.NONE]
    Ship.valid_ships = fleet_config


def _make_engine(
    agent_type: str,
    player_type: str = "random",
    player_placement_method: str | None = None,
    enable_ws: bool = False,
    headless: bool = True,
    checkpoint_path: str = "checkpoints/q_agent.pt",
    player_agent_type: str | None = None,
    ws_host: str = "localhost",
    ws_port: int = 8765,
    log_boards: bool = False,
    player_placement: str = "random",
    report_games: bool = False,
) -> GameEngine:
    agent_cls = AGENT_REGISTRY.get(agent_type)
    if agent_cls is None:
        raise ValueError(
            f"Unknown agent '{agent_type}'. Available: {list(AGENT_REGISTRY)}"
        )

    agent_kwargs: dict = {}
    if (
        checkpoint_path
        and "checkpoint_path" in inspect.signature(agent_cls.__init__).parameters
    ):
        agent_kwargs["checkpoint_path"] = checkpoint_path

    player_cls = AGENT_REGISTRY.get(player_agent_type) if player_agent_type else None

    return GameEngine(
        agent=agent_cls(**agent_kwargs),
        player_type=player_type,
        player_placement=player_placement,
        player_placement_method=player_placement_method,
        ws_host=ws_host,
        ws_port=ws_port,
        enable_ws=enable_ws,
        headless=headless,
        log_boards=log_boards,
        player_agent=player_cls() if player_cls else None,
        report_games=report_games,
    )


def run_games_headless(
    agent_type: str,
    player_placement_method: str | None = None,
    n_games: int = 100,
    checkpoint_path: str = "checkpoints/q_agent.pt",
    report_games: bool = False,
) -> list[dict]:
    """Run n_games headless agent-vs-random games and return per-game stats.

    Safe to call from Jupyter (runs in a fresh thread to avoid event-loop conflicts).
    """
    GameLogger.setup(console_level=logging.WARNING)
    _init_global_state()

    async def _inner() -> list[dict]:
        engine = _make_engine(
            agent_type=agent_type,
            player_placement_method=player_placement_method,
            checkpoint_path=checkpoint_path,
            report_games=report_games,
        )
        results = []
        for _ in range(n_games):
            await engine.run()
            results.append(
                {
                    "agent_won": engine.winner == "agent",
                    "turns": engine.agent_board.turn,
                    "agent_hits": engine.agent_score["hit"],
                    "agent_sunk": engine.agent_score["sunk"],
                    "player_hits": engine.player_score["hit"],
                    "player_sunk": engine.player_score["sunk"],
                }
            )
            engine.reset()
        return results

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, _inner()).result()


async def run_game() -> None:
    args = parse_args()

    GameLogger.setup(console_level=getattr(logging, args.log_level))

    if args.no_ws and args.player_type == "websocket":
        GameLogger.error(
            "--player-type websocket requires the WebSocket server. Remove --no-ws."
        )
        sys.exit(2)

    if args.player_placement != "random" and args.player_type not in (
        "websocket",
        "terminal",
    ):
        GameLogger.warn(
            "--player-placement is ignored when --player-type is not 'websocket' or 'terminal'"
        )

    if args.agent not in AGENT_REGISTRY:
        GameLogger.error(
            f"Unknown agent '{args.agent}'. Available: {list(AGENT_REGISTRY)}"
        )
        sys.exit(2)

    if args.player_type not in AGENT_REGISTRY and args.player_type not in (
        "websocket",
        "terminal",
    ):
        GameLogger.error(
            f"Unknown player type '{args.player_type}'. Available: {list(AGENT_REGISTRY)}, 'websocket', or 'terminal'"
        )
        sys.exit(2)

    valid_ships = set(ship.name for ship in ShipType if ship != ShipType.NONE)
    fleet_config = []
    for ship in args.fleet_config:
        if ship not in valid_ships:
            GameLogger.error(f"Invalid ship '{ship}'. Valid options: {valid_ships}")
            sys.exit(2)
        fleet_config.append(ShipType[ship])

    _init_global_state(board_size=args.board_size, fleet_config=fleet_config)
    GameLogger.debug(
        f"Selected ships for fleet: {[ship.name for ship in Ship.valid_ships]}"
    )

    engine = _make_engine(
        agent_type=args.agent,
        player_type=args.player_type,
        player_placement_method=args.player_placement_method,
        enable_ws=not args.no_ws,
        headless=args.headless,
        checkpoint_path=args.checkpoint,
        player_agent_type=(
            args.player_type if args.player_type in AGENT_REGISTRY else None
        ),
        ws_host=args.ws_host,
        ws_port=args.ws_port,
        log_boards=args.log_boards,
        player_placement=args.player_placement,
    )
    game_num = 1
    max_games = args.max_games
    win_dist = {"player": 0, "agent": 0}
    turns = []

    begin = time.time()
    while game_num <= max_games:
        GameLogger.info(f"GAME START — {game_num}")
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
    asyncio.run(run_game())
