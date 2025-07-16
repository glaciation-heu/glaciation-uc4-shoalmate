from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from timesim.clock import ClockDependency


router = APIRouter()


class TimeSim(BaseModel):
    cluster_id: str
    experiment_duration_sec: float | None
    experiment_tag: str
    is_active: bool
    minutes_per_hour: int
    virtual_time_sec: float | None


class TimeSimCreate(BaseModel):
    minutes_per_hour: int
    experiment_tag: str


@router.get("/", include_in_schema=False)
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url="/docs", status_code=307)


@router.get("/timesim")
async def get_timesim(clock: ClockDependency) -> TimeSim:
    """Get a time simulation state."""
    clock.tick()
    state = TimeSim(
        cluster_id="A",
        experiment_duration_sec=clock.real_sec,
        experiment_tag="experiment-1",
        is_active=clock.is_active,
        minutes_per_hour=clock.virtual_sec_per_minute,
        virtual_time_sec=clock.virtual_sec,
    )
    return state


@router.post(
    "/timesim",
    responses={409: {"description": "Time simulation is already active"}},
)
async def create_timesim(clock: ClockDependency, params: TimeSimCreate) -> TimeSim:
    """Start a new time simulation."""
    if clock.is_active:
        raise HTTPException(status_code=409, detail="Time simulation is already active")
    clock.virtual_sec_per_minute = params.minutes_per_hour
    clock.experiment_tag = params.experiment_tag
    clock.activate()
    return await get_timesim(clock)


@router.delete("/timesim")
async def delete_timesim(clock: ClockDependency) -> None:
    """Stop time simulation."""
    clock.deactivate()
