from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from timesim.clock import ClockDependency


router = APIRouter()


class State(BaseModel):
    experiment_duration_sec: float
    minutes_per_hour: int
    virtual_time_sec: float

    cluster_id: str = "A"
    experiment_tag: str = "experiment-1"
    output_bucket_capacity: int = 10


@router.get("/", include_in_schema=False)
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url="/docs", status_code=307)


@router.get("/timestamp")
async def get_timestamp(clock: ClockDependency) -> float:
    """
    Return a number of seconds since the beginning of simulated time.
    """
    clock.tick()
    return clock.virtual_sec


@router.get("/state")
async def get_state(clock: ClockDependency) -> State:
    """Return UI state"""
    clock.tick()
    state = State(
        experiment_duration_sec=clock.real_sec,
        minutes_per_hour=clock.virtual_sec_per_minute,
        virtual_time_sec=clock.virtual_sec,
    )
    return state
