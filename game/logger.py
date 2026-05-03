import logging
from datetime import datetime
from pathlib import Path

_LOG_DIR = Path(__file__).parent / "logs"
_FILE_FORMAT = "%(asctime)s %(levelname)-8s %(message)s"
_CONSOLE_FORMAT = "%(levelname)s: %(message)s"

_log = logging.getLogger("battleship")


class GameLogger:
    """
    Statically accessible logger. Call GameLogger.info() / .warn() / .error() / .debug()
    anywhere after GameLogger.setup() has been called from main.py.

    The level of each message is determined at call time by which method you use —
    no global threshold is imposed on the file output. The console threshold is the
    only filter, controlled by --log-level at startup.
    """

    @classmethod
    def setup(cls, console_level: int = logging.WARNING) -> None:
        """Configure handlers. Called once from main.py at process start."""
        _LOG_DIR.mkdir(exist_ok=True)
        log_file = _LOG_DIR / f"battleship_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

        _log.setLevel(logging.DEBUG)  # pass everything to handlers; handlers decide

        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)  # file captures all levels — level set at call time
        fh.setFormatter(logging.Formatter(_FILE_FORMAT))
        _log.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(console_level)  # console respects --log-level (default WARNING)
        ch.setFormatter(logging.Formatter(_CONSOLE_FORMAT))
        _log.addHandler(ch)

    @classmethod
    def debug(cls, msg: str, *args) -> None:
        _log.debug(msg, *args)

    @classmethod
    def info(cls, msg: str, *args) -> None:
        _log.info(msg, *args)

    @classmethod
    def warn(cls, msg: str, *args) -> None:
        _log.warning(msg, *args)

    @classmethod
    def error(cls, msg: str, *args) -> None:
        _log.error(msg, *args)
