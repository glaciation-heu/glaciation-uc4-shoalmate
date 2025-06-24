from datetime import timedelta

import pytest

from shoalmate.allocator import Allocator
from shoalmate.settings import ClusterIDEnum


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
            id="Stays on current cluster when high rank"
        ),
        pytest.param(
            ClusterIDEnum.CLUSTER_B,
            {
                ClusterIDEnum.CLUSTER_A: 0.9,
                ClusterIDEnum.CLUSTER_B: 0.5,
                ClusterIDEnum.CLUSTER_C: 0.3,
            },
            ClusterIDEnum.CLUSTER_A,
            id="Change cluster when high rank"
        ),
        pytest.param(
            ClusterIDEnum.CLUSTER_B,
            {
                ClusterIDEnum.CLUSTER_A: 0.0009,
                ClusterIDEnum.CLUSTER_B: 0.0005,
                ClusterIDEnum.CLUSTER_C: 0.0003,
            },
            ClusterIDEnum.CLUSTER_B,
            id="Do not change cluster when small ranks"
        ),
    ]
)
def test__call__valid_response(mocker, current_cluster_id, ranks, expected_result):
    # Arrange
    mock_ranker = mocker.patch('shoalmate.allocator.Ranker')
    mock_ranker.return_value.get.return_value = ranks
    mock_get_settings = mocker.patch('shoalmate.allocator.get_settings')
    mock_get_settings.return_value.rank_similarity_threshold = 0.1
    mock_get_settings.return_value.cluster_id = current_cluster_id
    time_offset = timedelta(hours=1)

    # Act
    allocator = Allocator()
    actual_result = allocator.get_target_cluster(time_offset)

    # Assert
    assert actual_result == expected_result
