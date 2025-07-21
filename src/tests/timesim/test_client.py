import subprocess

import pytest
from pydantic import HttpUrl

from timesim.timesim import get_timesim_state
from timesim.schemas import Timesim


@pytest.fixture
def fastapi_app():
    process = subprocess.Popen(
        [
            "fastapi",
            "run",
            "src/timesim/main.py",
            "--host",
            "127.0.0.1",
            "--port",
            "8002",
        ],
        stderr=subprocess.PIPE,
    )
    while "Application startup complete" not in process.stderr.readline().decode(
        "utf-8"
    ):
        pass
    yield
    process.terminate()
    process.wait()


def test_client(fastapi_app):
    url = HttpUrl("http://127.0.0.1:8002")
    result = get_timesim_state(url)
    assert type(result) is Timesim
