import pytest
from starlette.testclient import TestClient

from timesim.domain import _get_experiment
from timesim.main import app


@pytest.fixture
def client():
    _get_experiment.cache_clear()
    return TestClient(app)
