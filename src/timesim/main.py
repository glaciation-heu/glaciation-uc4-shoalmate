from fastapi import FastAPI

from fastapi.responses import HTMLResponse
from timesim.api import router as api_router


app = FastAPI(
    title="Time Simulator API", swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)
app.include_router(api_router, prefix="/api", tags=["API"])


@app.get("/", include_in_schema=False)
async def root():
    return HTMLResponse(content="<h1>Hello, World!</h1>")
