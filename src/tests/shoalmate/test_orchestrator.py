from typing import NamedTuple

import pytest

from shoalmate.client import get_client
from shoalmate.orchestrator import Orchestrator
from shoalmate.settings import ClusterIDEnum, get_settings


class ObjectsCount(NamedTuple):
    input_bucket: int
    output_bucket: int


class ClusterCounts(NamedTuple):
    cluster_a: ObjectsCount
    cluster_b: ObjectsCount
    cluster_c: ObjectsCount


def get_bucket_counts() -> ClusterCounts:
    result = []
    settings = get_settings()
    for cluster_id in ClusterIDEnum:
        client = get_client(cluster_id)
        object_counts = ObjectsCount(
            len(list(client.list_objects(settings.input_bucket_chunks))),
            len(list(client.list_objects(settings.output_bucket)))
        )
        result.append(object_counts)
    return ClusterCounts(*result)


@pytest.fixture
def minio_clusters_mock(minio_mock, settings_mock):
    for cluster_id in ClusterIDEnum:
        client = get_client(cluster_id)
        client.make_bucket(settings_mock.input_bucket_chunks)
        client.make_bucket(settings_mock.output_bucket)


@pytest.fixture
def orchestrator_mock(minio_clusters_mock , ranker_mock):
    orchestrator = Orchestrator()
    orchestrator._sleep_time = 0
    return orchestrator


def test__run_when_no_objects__no_action(orchestrator_mock):
    orchestrator_mock.run_once()
    expected = ClusterCounts(
        ObjectsCount(0, 0),
        ObjectsCount(0, 0),
        ObjectsCount(0, 0),
    )
    assert get_bucket_counts() == expected