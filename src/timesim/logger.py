import sys
from logging import Logger, getLogger, INFO, StreamHandler, Formatter
from typing import Annotated

from fastapi import Depends


def get_logger() -> Logger:
    logger = getLogger("timesim")
    logger.setLevel(INFO)
    if not logger.hasHandlers():
        handler = StreamHandler(sys.stdout)
        formatter = Formatter("%(levelname)10s   %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


LoggerDependency = Annotated[Logger, Depends(get_logger)]
