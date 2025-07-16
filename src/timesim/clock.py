from datetime import datetime
from functools import lru_cache
from typing import Annotated

from fastapi import Depends


class Clock:
    """Clock runs time simulation."""

    start_time: datetime
    minutes_per_hour: int = 60

    def __init__(self) -> None:
        self.start_time = datetime.now()

    def get_virtual_sec(self) -> float:
        """Return current virtual time in seconds."""
        current_time = datetime.now()
        real_delta = current_time - self.start_time
        sim_delta = real_delta / self.minutes_per_hour * 60
        return sim_delta.total_seconds()


@lru_cache
def _get_clock() -> Clock:
    return Clock()


ClockDependency = Annotated[Clock, Depends(_get_clock)]
