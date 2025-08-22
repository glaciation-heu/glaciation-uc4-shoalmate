from typing import Annotated

from pydantic import BaseModel, Field


class Timesim(BaseModel):
    cluster_id: str
    experiment_duration_sec: float | None
    experiment_tag: str
    is_active: bool
    minutes_per_hour: float
    virtual_time_sec: float | None
    multicluster: int


class ExperimentCreate(BaseModel):
    minutes_per_hour: Annotated[int, Field(gt=0, lt=61)]
    experiment_tag: Annotated[str, Field(min_length=5, max_length=32)]
    multicluster: Annotated[int, Field(gt=0, lt=2)]
