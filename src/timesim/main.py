from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI(title="TimeSim API")


@app.get("/", include_in_schema=False)
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url="/docs", status_code=307)


@app.get("/timestamp")
async def get_timestamp() -> int:
    """
    Return a number of seconds since the beginning of simulated time.
    """
    return 42
