import logging
from pathlib import Path

from logger import AppLogger


class GameLogger(AppLogger):
    _log_dir = Path(__file__).parent / "logs"

    @classmethod
    def setup(cls, console_level: int = logging.INFO) -> None:
        super().setup(name="game", run_name="game", console_level=console_level)
