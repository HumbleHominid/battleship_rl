import logging
from datetime import datetime
from pathlib import Path

_LOG_DIR = Path(__file__).parent / "logs"
_FILE_FORMAT = "%(asctime)s %(levelname)-8s %(message)s"

_log = logging.getLogger("training")


class TrainingLogger:
    """
    Statically accessible logger for training scripts.

    Call TrainingLogger.setup(run_name="pretrain") once at the top of main().
    The log file is written to training/logs/<run_name>_<timestamp>.log.
    Console output shows the raw message; the file captures level + timestamp.
    """

    log_file: Path | None = None

    @classmethod
    def setup(cls, run_name: str = "train", console_level: int = logging.INFO) -> None:
        _LOG_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        cls.log_file = _LOG_DIR / f"{run_name}_{timestamp}.log"

        _log.setLevel(logging.DEBUG)

        fh = logging.FileHandler(cls.log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(_FILE_FORMAT))
        _log.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(console_level)
        ch.setFormatter(logging.Formatter("%(message)s"))
        _log.addHandler(ch)

    @classmethod
    def close(cls) -> None:
        for handler in list(_log.handlers):
            if isinstance(handler, logging.FileHandler):
                handler.flush()
                handler.close()
                _log.removeHandler(handler)

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
