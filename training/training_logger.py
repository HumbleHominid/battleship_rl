import logging
from pathlib import Path

from logger import AppLogger


class TrainingLogger(AppLogger):
    _log_dir = Path(__file__).parent / "logs"

    @classmethod
    def setup(cls, run_name: str = "train", console_level: int = logging.INFO) -> None:
        super().setup(name="training", run_name=run_name, console_level=console_level)
