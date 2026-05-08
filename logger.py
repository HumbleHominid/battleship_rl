import logging
from datetime import datetime
from pathlib import Path
from typing import ClassVar

_FILE_FORMAT = "%(asctime)s %(levelname)-8s %(message)s"


class AppLogger:
    _log_dir: ClassVar[Path]
    log_file: ClassVar[Path | None] = None
    _log: ClassVar[logging.Logger | None] = None

    @classmethod
    def setup(cls, name: str, run_name: str = "run", console_level: int = logging.INFO) -> None:
        cls._log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        cls.log_file = cls._log_dir / f"{run_name}_{timestamp}.log"

        cls._log = logging.getLogger(name)
        cls._log.setLevel(logging.DEBUG)

        fh = logging.FileHandler(cls.log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(_FILE_FORMAT))
        cls._log.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(console_level)
        ch.setFormatter(logging.Formatter("%(message)s"))
        cls._log.addHandler(ch)

    @classmethod
    def close(cls) -> None:
        if cls._log is None:
            return
        for handler in list(cls._log.handlers):
            if isinstance(handler, logging.FileHandler):
                handler.flush()
                handler.close()
                cls._log.removeHandler(handler)

    @classmethod
    def debug(cls, msg: str, *args) -> None:
        cls._log.debug(msg, *args)

    @classmethod
    def info(cls, msg: str, *args) -> None:
        cls._log.info(msg, *args)

    @classmethod
    def warn(cls, msg: str, *args) -> None:
        cls._log.warning(msg, *args)

    @classmethod
    def error(cls, msg: str, *args) -> None:
        cls._log.error(msg, *args)
