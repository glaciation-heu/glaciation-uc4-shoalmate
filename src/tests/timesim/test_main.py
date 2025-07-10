import pytest
from fastapi.testclient import TestClient

from timesim.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test__get_root__redirects_to_docs(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


def test__get_timestamp__timestamp_returned(client):
    response = client.get("/timestamp")
    assert response.status_code == 200
    assert response.json() == 42
