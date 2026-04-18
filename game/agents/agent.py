import random
from typing import Optional

from game.game_board import GameBoard


class RLAgent:
    """
    Stub RL agent. Simulates the WebSocket client the real agent will be.

    In automated mode (no WS agent connected), GameEngine uses select_move() directly
    for random baseline play. The real agent will be a separate process that connects
    to the game's WebSocket server, receives observations, and sends move commands.

    WebSocket client interface methods are stubbed here to document the expected
    architecture and raise NotImplementedError until implemented.
    """

    def __init__(self) -> None:
        self._untried_cells: list[tuple[int, int]] = [
            (r, c) for r in range(10) for c in range(10)
        ]
        self._rng = random.Random()

    def select_move(self, board_state: dict) -> str:
        """
        Stub: pick a random untried cell and return its coordinate string (e.g. 'C7').
        Real implementation: use board_state as the RL observation, run the policy network.
        """
        if not self._untried_cells:
            raise RuntimeError("No untried cells remain — game should already be over")
        cell = self._rng.choice(self._untried_cells)
        self._untried_cells.remove(cell)
        return GameBoard.format_coordinate(cell[0], cell[1])

    def receive_result(
        self, coordinate: str, result: str, ship_sunk: Optional[str]
    ) -> None:
        """
        Stub: record the result of the agent's last move.
        Real implementation: add (state, action, reward, next_state) to replay buffer;
        optionally trigger a training step.
        """
        pass

    def reset(self) -> None:
        """Reset agent state for a new game episode."""
        self._untried_cells = [(r, c) for r in range(10) for c in range(10)]

    # ------------------------------------------------------------------
    # WebSocket client interface stubs
    # ------------------------------------------------------------------
    # The real RL agent will be a separate process that:
    #   1. Connects to the game's WebSocket server
    #   2. Sends {"type": "hello", "role": "rl_agent"}
    #   3. Receives {"type": "agent_view", ...} observations each turn
    #   4. Sends {"type": "move", "coordinate": "B5"} move commands
    #   5. Receives {"type": "move_ack", ...} results
    # ------------------------------------------------------------------

    async def connect_to_server(self, uri: str) -> None:
        """
        Connect this agent to a running GameWebSocketServer.
        Real implementation: websockets.connect(uri), send role announcement.
        """
        raise NotImplementedError(
            "Real RL agent uses a WebSocket client. "
            "Use RLAgent.select_move() directly for stub-based play."
        )

    async def send_move_via_websocket(self, coordinate: str) -> None:
        """Send a move command JSON to the server over WebSocket."""
        raise NotImplementedError

    async def receive_ack_via_websocket(self) -> dict:
        """Await a move_ack JSON message from the server."""
        raise NotImplementedError
