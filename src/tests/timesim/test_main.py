import pytest
from fastapi.testclient import TestClient

from timesim.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test__get_root__redirects_to_docs(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"


def test__get_api_root__redirects_to_docs(client):
    response = client.get("/api/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


def test__get_api_timesim__timestamp_returned(client):
    response = client.get("/api/timesim")
    assert response.status_code == 200
    actual = response.json()
    assert len(actual) == 5
    assert actual["cluster_id"] == "A"
    assert actual["experiment_duration_sec"] == 0
    assert actual["experiment_tag"] == "experiment-1"
    assert actual["minutes_per_hour"] == 60
    assert actual["virtual_time_sec"] == 0
