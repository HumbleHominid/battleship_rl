import logging
from datetime import datetime
from pathlib import Path

_LOG_DIR = Path(__file__).parent / "logs"


def setup_logging(run_name: str, console_level: int | str = logging.INFO) -> Path:
    """Send all logs to a timestamped file and console_level and up to stderr."""
    _LOG_DIR.mkdir(exist_ok=True)
    log_file = _LOG_DIR / f"{run_name}_{datetime.now():%Y-%m-%d_%H-%M-%S}.log"

    console = logging.StreamHandler()
    console.setLevel(console_level)
    console.setFormatter(logging.Formatter("%(message)s"))

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(message)s",
        handlers=[console, logging.FileHandler(log_file, encoding="utf-8")],
    )
    return log_file
