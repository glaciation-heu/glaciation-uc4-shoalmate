from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from timesim.clock import ClockDependency


router = APIRouter()


class Timesim(BaseModel):
    cluster_id: str
    experiment_duration_sec: float | None
    experiment_tag: str
    is_active: bool
    minutes_per_hour: int
    virtual_time_sec: float | None


class ExperimentCreate(BaseModel):
    minutes_per_hour: Annotated[int, Field(gt=0, lt=61)]
    experiment_tag: Annotated[str, Field(min_length=5, max_length=32)]


@router.get("/", include_in_schema=False)
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url="/docs", status_code=307)


@router.get("/timesim")
async def get_timesim(clock: ClockDependency) -> Timesim:
    """Get a time simulation state."""
    clock.tick()
    state = Timesim(
        cluster_id="A",
        experiment_duration_sec=clock.real_sec,
        experiment_tag="experiment-1",
        is_active=clock.is_active,
        minutes_per_hour=clock.virtual_sec_per_real_minute,
        virtual_time_sec=clock.virtual_sec,
    )
    return state


@router.post(
    "/timesim/experiment",
    responses={409: {"description": "Time simulation is already active"}},
)
async def create_experiment(clock: ClockDependency, params: ExperimentCreate) -> None:
    """Start a new time simulation experiment."""
    if clock.is_active:
        raise HTTPException(status_code=409, detail="Time simulation is already active")
    clock.virtual_sec_per_real_minute = params.minutes_per_hour
    clock.experiment_tag = params.experiment_tag
    clock.activate()
    return None


@router.delete("/timesim/experiment")
async def delete_experiment(clock: ClockDependency) -> None:
    """Stop time simulation experiment."""
    clock.deactivate()
