from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from timesim.domain import ExperimentDependency
from timesim.schemas import Timesim, ExperimentCreate

router = APIRouter()


@router.get("/", include_in_schema=False)
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url="/docs", status_code=307)


@router.get("/timesim")
async def get_timesim(experiment: ExperimentDependency) -> Timesim:
    """Get a time simulation state."""
    experiment.clock.tick()
    result = Timesim(
        cluster_id="A",
        experiment_duration_sec=experiment.clock.real_sec,
        experiment_tag=experiment.experiment_tag,
        is_active=experiment.clock.is_active,
        minutes_per_hour=experiment.clock.virtual_sec_per_real_minute,
        virtual_time_sec=experiment.clock.virtual_sec,
        multicluster=experiment.multicluster,
        scores=experiment.scores,
    )
    return result


@router.post(
    "/timesim/experiment",
    responses={409: {"description": "Time simulation is already active"}},
)
async def create_experiment(
    experiment: ExperimentDependency, params: ExperimentCreate
) -> None:
    """Start a new time simulation experiment."""
    experiment.experiment_tag = params.experiment_tag
    experiment.multicluster = params.multicluster
    experiment.scores = params.scores
    clock = experiment.clock
    if clock.is_active:
        raise HTTPException(status_code=409, detail="Time simulation is already active")
    clock.virtual_sec_per_real_minute = params.minutes_per_hour
    clock.experiment_tag = params.experiment_tag
    clock.activate()
    return None


@router.delete("/timesim/experiment")
async def delete_experiment(experiment: ExperimentDependency) -> None:
    """Stop time simulation experiment."""
    experiment.clock.deactivate()
