from datetime import timedelta

import pytest

from shoalmate.allocator import Allocator
from shoalmate.settings import ClusterIDEnum


@pytest.fixture
def ranker_mock(mocker):
    ranker_mock = mocker.patch("shoalmate.allocator.Ranker")
    return ranker_mock.return_value


@pytest.mark.parametrize(
    "current_cluster_id, ranks, expected_result",
    [
        pytest.param(
            ClusterIDEnum.CLUSTER_A,
            {
                ClusterIDEnum.CLUSTER_A: 0.9,
                ClusterIDEnum.CLUSTER_B: 0.5,
                ClusterIDEnum.CLUSTER_C: 0.3,
            },
            ClusterIDEnum.CLUSTER_A,
            id="Stays on current cluster when high rank",
        ),
        pytest.param(
            ClusterIDEnum.CLUSTER_B,
            {
                ClusterIDEnum.CLUSTER_A: 0.9,
                ClusterIDEnum.CLUSTER_B: 0.5,
                ClusterIDEnum.CLUSTER_C: 0.3,
            },
            ClusterIDEnum.CLUSTER_A,
            id="Change cluster when high rank",
        ),
        pytest.param(
            ClusterIDEnum.CLUSTER_B,
            {
                ClusterIDEnum.CLUSTER_A: 0.0009,
                ClusterIDEnum.CLUSTER_B: 0.0005,
                ClusterIDEnum.CLUSTER_C: 0.0003,
            },
            ClusterIDEnum.CLUSTER_B,
            id="Do not change cluster when small ranks",
        ),
    ],
)
def test__call__valid_response(
    mocker,
    settings_mock,
    ranker_mock,
    current_cluster_id,
    ranks,
    expected_result,
):
    # Arrange
    ranker_mock.get.return_value = ranks
    settings_mock.cluster_id = current_cluster_id
    time_offset = timedelta(hours=1)

    # Act
    allocator = Allocator()
    actual_result = allocator.get_target_cluster(time_offset)

    # Assert
    assert actual_result == expected_result
