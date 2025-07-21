import httpx
from pydantic import HttpUrl

from timesim.schemas import Timesim


def get_timesim_state(base_url: HttpUrl) -> Timesim:
    response = httpx.get(str(base_url) + "api/timesim")
    return Timesim.model_validate_json(response.read())
