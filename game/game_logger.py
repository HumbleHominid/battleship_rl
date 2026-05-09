import logging
from pathlib import Path

from app_logger import AppLogger


class GameLogger(AppLogger):
    _log_dir = Path(__file__).parent / "logs"

    @classmethod
    def setup(
        cls,
        name: str = "game",
        run_name: str = "game",
        console_level: int = logging.INFO,
    ) -> None:
        super().setup(name=name, run_name=run_name, console_level=console_level)
