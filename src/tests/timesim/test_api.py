import pytest
from httpx import Response
from pytest import approx


DEFAULT_CREATE_ARGS = {
    "experiment_tag": "experiment-1",
    "minutes_per_hour": 5,
}


@pytest.fixture
def create_timesim(client) -> Response:
    response = client.post("/api/timesim", json=DEFAULT_CREATE_ARGS)
    return response


def test__get_api_root__redirects_to_docs(client):
    response = client.get("/api/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


def test__call_post_once__timesim_activated(create_timesim):
    response = create_timesim
    assert response.status_code == 200
    actual = response.json()
    assert len(actual) == 6
    assert actual["cluster_id"] == "A"
    assert 0 < actual["experiment_duration_sec"] < 0.01
    assert actual["experiment_tag"] == "experiment-1"
    assert actual["is_active"] is True
    assert actual["minutes_per_hour"] == 5
    assert 0 < actual["virtual_time_sec"] < 0.01


def test__call_get__valid_response(create_timesim, client):
    response = client.get("/api/timesim")

    assert response.status_code == 200
    expected = create_timesim.json()
    actual = response.json()
    assert len(actual) == len(expected)
    assert expected["cluster_id"] == actual["cluster_id"]
    assert expected["experiment_duration_sec"] - actual[
        "experiment_duration_sec"
    ] == approx(0, abs=0.01)
    assert expected["experiment_tag"] == actual["experiment_tag"]
    assert expected["is_active"] == actual["is_active"]
    assert expected["minutes_per_hour"] == actual["minutes_per_hour"]
    assert expected["virtual_time_sec"] - actual["virtual_time_sec"] == approx(
        0, abs=0.01
    )


@pytest.mark.skip(reason="Not implemented yet")  # TODO
def test__call_post_twice__error(create_timesim, client):
    response = client.post("/api/timesim", json=DEFAULT_CREATE_ARGS)
    assert response.status_code == 409


def test__call_delete_once__deactivated(create_timesim, client):
    response = client.delete("/api/timesim")
    assert response.status_code == 200
    assert response.json() is None


def test__call_delete_twice__deactivated(create_timesim, client):
    client.delete("/api/timesim")

    response = client.delete("/api/timesim")

    assert response.status_code == 200
    assert response.json() is None
