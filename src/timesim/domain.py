from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from logging import Logger
from typing import Annotated

from fastapi import Depends

from timesim.logger import LoggerDependency


class Clock:
    """Clock runs time simulation."""

    _logger: Logger

    _start_time: datetime | None = None
    _now: datetime | None = None

    virtual_sec_per_real_minute: int = 60

    def __init__(self, logger: Logger):
        self._logger = logger

    def activate(self):
        if self._start_time:
            raise RuntimeError("Clock is already started")
        self._start_time = datetime.now()
        self._logger.info("Clock started at %s", self._start_time)

    def deactivate(self):
        self._start_time = None
        self._now = None
        self._logger.info("Clock reset")

    def tick(self):
        if self._start_time:
            self._now = datetime.now()
            self._logger.info("Clock ticked at %s", self._now)

    @property
    def is_active(self) -> bool:
        return self._start_time is not None

    @property
    def virtual_sec(self) -> float | None:
        result = None
        if self.is_active:
            result = self.real_sec / self.virtual_sec_per_real_minute * 60
        return result

    @property
    def real_sec(self) -> float | None:
        result = None
        if self.is_active:
            delta = self._now - self._start_time
            result = delta.total_seconds()
        return result


@dataclass
class Experiment:
    clock: Clock
    experiment_tag: str
    multicluster: int
    scores: int


@lru_cache
def _get_experiment(logger: LoggerDependency) -> Experiment:
    clock = Clock(logger)
    return Experiment(clock=clock, experiment_tag="", multicluster=0, scores=0)


ExperimentDependency = Annotated[Experiment, Depends(_get_experiment)]
