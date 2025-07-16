import pytest
from starlette.testclient import TestClient

from timesim.clock import _get_clock
from timesim.main import app


@pytest.fixture
def client():
    _get_clock.cache_clear()
    return TestClient(app)
