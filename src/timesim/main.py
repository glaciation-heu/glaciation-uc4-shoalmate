from fastapi import FastAPI

from fastapi.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

from timesim.api import router as api_router


app = FastAPI(
    title="Time Simulator API", swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)
app.include_router(api_router, prefix="/api", tags=["API"])
app.mount("/static", StaticFiles(directory="src/timesim/static"), name="static")


@app.get("/", include_in_schema=False)
async def root():
    with open("src/timesim/static/index.html", "r") as file:
        return HTMLResponse(content=file.read())
