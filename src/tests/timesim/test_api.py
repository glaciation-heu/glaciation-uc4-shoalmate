import pytest
from httpx import Response

from timesim.schemas import Timesim

DEFAULT_CREATE_ARGS = {
    "experiment_tag": "experiment-1",
    "minutes_per_hour": 5,
}


@pytest.fixture
def create_experiment(client) -> Response:
    response = client.post("/api/timesim/experiment", json=DEFAULT_CREATE_ARGS)
    return response


def test__get_root__redirects_to_docs(client):
    response = client.get("/api/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


def test__post_experiment_once__experiment_activated(create_experiment):
    response = create_experiment
    assert response.status_code == 200
    assert response.json() is None


def test__get_timesim_when_created__valid_response(create_experiment, client):
    response = client.get("/api/timesim")

    assert response.status_code == 200
    actual = response.json()
    assert len(actual) == 6
    assert actual["cluster_id"] == "A"
    assert 0 < actual["experiment_duration_sec"] < 0.1
    assert actual["experiment_tag"] == "experiment-1"
    assert actual["is_active"] is True
    assert actual["minutes_per_hour"] == 5
    assert 0 < actual["virtual_time_sec"] < 0.1


def test__get_timesim_when_not_created__valid_response(client):
    response = client.get("/api/timesim")

    assert response.status_code == 200
    actual = Timesim.model_validate_json(response.text)
    expected = Timesim(
        cluster_id="A",
        experiment_duration_sec=None,
        experiment_tag="",
        is_active=False,
        minutes_per_hour=60,
        virtual_time_sec=None,
    )
    assert actual == expected


def test__post_experiment_twice__error(create_experiment, client):
    response = client.post("/api/timesim/experiment", json=DEFAULT_CREATE_ARGS)
    assert response.status_code == 409


def test__delete_experiment_once__deactivated(create_experiment, client):
    response = client.delete("/api/timesim/experiment")
    assert response.status_code == 200
    assert response.json() is None


def test__delete_experiment_twice__deactivated(create_experiment, client):
    client.delete("/api/timesim/experiment")

    response = client.delete("/api/timesim/experiment")

    assert response.status_code == 200
    assert response.json() is None
