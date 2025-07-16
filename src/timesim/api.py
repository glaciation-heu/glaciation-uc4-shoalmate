from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from timesim.clock import ClockDependency


router = APIRouter()


@router.get("/", include_in_schema=False)
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url="/docs", status_code=307)


@router.get("/timestamp")
async def get_timestamp(clock: ClockDependency) -> float:
    """
    Return a number of seconds since the beginning of simulated time.
    """
    return clock.get_virtual_sec()
