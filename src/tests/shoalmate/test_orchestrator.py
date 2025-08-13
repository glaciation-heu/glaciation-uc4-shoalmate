from typing import NamedTuple

import pytest

from shoalmate.clients.minio import get_client
from shoalmate.orchestrator import Orchestrator
from shoalmate.ranker import RankerDebugInfo
from shoalmate.settings import ClusterIDEnum, get_settings
from timesim.schemas import Timesim


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
            len(list(client.list_objects(settings.output_bucket))),
        )
        result.append(object_counts)
    return ClusterCounts(*result)


@pytest.fixture
def minio_clusters_mock(minio_mock, settings_mock):
    get_client.cache_clear()
    for cluster_id in ClusterIDEnum:
        client = get_client(cluster_id)
        client.make_bucket(settings_mock.input_bucket_chunks)
        client.make_bucket(settings_mock.output_bucket)


@pytest.fixture
def allocator_mock(mocker):
    allocator_mock = mocker.patch("shoalmate.orchestrator.Allocator")
    allocator_mock.return_value.get_target_cluster.return_value = (
        ClusterIDEnum.CLUSTER_A,
        RankerDebugInfo(0),
    )
    return allocator_mock.return_value


@pytest.fixture
def orchestrator_mock(mocker, minio_clusters_mock, allocator_mock):
    mocker.patch(
        "shoalmate.orchestrator.get_timesim_state",
        return_value=Timesim(
            cluster_id="A",
            experiment_duration_sec=1,
            experiment_tag="tag1",
            is_active=True,
            minutes_per_hour=60,
            virtual_time_sec=1,
        ),
    )
    orchestrator = Orchestrator()
    orchestrator._sleep_time = 0
    return orchestrator


@pytest.mark.parametrize("allocated_cluster", ClusterIDEnum)
def test__run_with_one_object__moved_to_the_right_cluster(
    orchestrator_mock, allocator_mock, allocated_cluster
):
    # Arrange
    client = get_client(ClusterIDEnum.CLUSTER_A)
    client.put_object(
        bucket_name=get_settings().input_bucket_chunks,
        object_name="SCADA_siteA_year1_1.parquet",
        data=bytes(),
        length=0,
    )
    allocator_mock.get_target_cluster.return_value = (
        allocated_cluster,
        RankerDebugInfo(0),
    )

    # Act
    orchestrator_mock.run_once()

    # Assert
    expected = ClusterCounts(
        *(
            ObjectsCount(0, 1) if cluster == allocated_cluster else ObjectsCount(0, 0)
            for cluster in ClusterIDEnum
        )
    )
    assert get_bucket_counts() == expected


def test__run_with_no_objects__nothing_moved(orchestrator_mock):
    # Arrange
    client = get_client(ClusterIDEnum.CLUSTER_B)
    client.put_object(
        bucket_name=get_settings().input_bucket_chunks,
        object_name="SCADA_siteA_year1_1.parquet",
        data=bytes(),
        length=0,
    )

    # Act
    orchestrator_mock.run_once()

    # Assert
    expected = ClusterCounts(
        ObjectsCount(0, 0),
        ObjectsCount(1, 0),
        ObjectsCount(0, 0),
    )
    assert get_bucket_counts() == expected


def test__run_when_target_is_busy__wait_while_busy(mocker, orchestrator_mock):
    # Arrange
    sleep_mock = mocker.patch("shoalmate.orchestrator.sleep")
    mocker.patch.object(orchestrator_mock, "_get_output_count", side_effect=[11, 10])
    client = get_client(ClusterIDEnum.CLUSTER_A)
    client.put_object(
        bucket_name=get_settings().input_bucket_chunks,
        object_name="SCADA_siteA_year1_1.parquet",
        data=bytes(),
        length=0,
    )

    # Act
    orchestrator_mock.run_once()

    # Assert
    sleep_mock.assert_called_once_with(orchestrator_mock._sleep_time)


def test__call_get_output_count__return_count(orchestrator_mock):
    # Arrange
    client = get_client(ClusterIDEnum.CLUSTER_A)
    client.put_object(
        bucket_name=get_settings().output_bucket,
        object_name="test_object.parquet",
        data=bytes(),
        length=0,
    )

    # Act
    result = orchestrator_mock._get_output_count(ClusterIDEnum.CLUSTER_A)

    # Assert
    assert result == 1


def test__call_get_active_timesim_state_when_not_active__wait(
    mocker, settings_mock, orchestrator_mock
):
    # Arrange
    state_1 = Timesim(
        cluster_id="A",
        experiment_duration_sec=None,
        experiment_tag="tag1",
        is_active=False,
        minutes_per_hour=60,
        virtual_time_sec=None,
    )
    state_2 = Timesim(
        cluster_id="A",
        experiment_duration_sec=1,
        experiment_tag="tag1",
        is_active=True,
        minutes_per_hour=60,
        virtual_time_sec=1,
    )
    mocker.patch(
        "shoalmate.orchestrator.get_timesim_state",
        side_effect=[state_1, state_2],
    )
    sleep_mock = mocker.patch("shoalmate.orchestrator.sleep")

    # Act
    result = orchestrator_mock._get_active_timesim_state()

    # Assert
    sleep_mock.assert_called_once_with(orchestrator_mock._sleep_time)
    assert result == state_2
