import logging
from datetime import datetime
from functools import lru_cache
from typing import Annotated

from fastapi import Depends


class Clock:
    """Clock runs time simulation."""

    _start_time: datetime
    _now: datetime

    virtual_sec_per_minute: int = 60

    def tick(self):
        if not hasattr(self, "_start_time"):
            self._start_time = datetime.now()
            self._now = self._start_time
            logging.info("New clock started")
        else:
            self._now = datetime.now()
        logging.info("Clock ticked at %s", self._now)

    @property
    def virtual_sec(self) -> float:
        result = self.real_sec
        return result * self.virtual_sec_per_minute / 60

    @property
    def real_sec(self) -> float:
        delta = self._now - self._start_time
        return delta.total_seconds()


@lru_cache
def _get_clock() -> Clock:
    return Clock()


ClockDependency = Annotated[Clock, Depends(_get_clock)]
