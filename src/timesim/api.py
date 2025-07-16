from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from timesim.clock import ClockDependency


router = APIRouter()


class TimeSim(BaseModel):
    experiment_duration_sec: float
    minutes_per_hour: int
    virtual_time_sec: float

    cluster_id: str = "A"
    experiment_tag: str = "experiment-1"


@router.get("/", include_in_schema=False)
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url="/docs", status_code=307)


@router.get("/timesim")
async def get_timesim(clock: ClockDependency) -> TimeSim:
    """Get state of the time simulator."""
    clock.tick()
    state = TimeSim(
        experiment_duration_sec=clock.real_sec,
        minutes_per_hour=clock.virtual_sec_per_minute,
        virtual_time_sec=clock.virtual_sec,
    )
    return state
