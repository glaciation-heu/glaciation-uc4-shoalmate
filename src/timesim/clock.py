from datetime import datetime
from functools import lru_cache
from logging import Logger
from typing import Annotated

from fastapi import Depends

from timesim.logger import LoggerDependency


class Clock:
    """Clock runs time simulation."""

    _start_time: datetime
    _now: datetime
    _logger: Logger

    virtual_sec_per_minute: int = 60

    def __init__(self, logger: Logger):
        self._logger = logger

    def tick(self):
        if not hasattr(self, "_start_time"):
            self._start_time = datetime.now()
            self._now = self._start_time
            self._logger.info("New clock started")
        else:
            self._now = datetime.now()
        self._logger.info("Clock ticked at %s", self._now)

    @property
    def virtual_sec(self) -> float:
        result = self.real_sec
        return result * self.virtual_sec_per_minute / 60

    @property
    def real_sec(self) -> float:
        delta = self._now - self._start_time
        return delta.total_seconds()


@lru_cache
def _get_clock(logger: LoggerDependency) -> Clock:
    return Clock(logger)


ClockDependency = Annotated[Clock, Depends(_get_clock)]
