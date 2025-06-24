from datetime import timedelta
from unittest.mock import patch

import pytest

from shoalmate.index import Ranker
from shoalmate.settings import ClusterIDEnum

TEST_TIMELINE = (
    {
        ClusterIDEnum.CLUSTER_A: 0.1,
        ClusterIDEnum.CLUSTER_B: 0.2,
        ClusterIDEnum.CLUSTER_C: 0.3,
    },
    {
        ClusterIDEnum.CLUSTER_A: 0.4,
        ClusterIDEnum.CLUSTER_B: 0.5,
        ClusterIDEnum.CLUSTER_C: 0.6,
    },
    {
        ClusterIDEnum.CLUSTER_A: 0.7,
        ClusterIDEnum.CLUSTER_B: 0.8,
        ClusterIDEnum.CLUSTER_C: 0.9,
    },
)


@pytest.fixture(autouse=True)
def loader_mock():
    with patch('shoalmate.index._Loader') as mock_loader_class:
        mock_loader_instance = mock_loader_class.return_value
        mock_loader_instance.load.return_value = TEST_TIMELINE
        yield mock_loader_instance


@pytest.mark.parametrize("hours_offset", [0, 1, 2])
def test__call_get_with_valid_hour_offset__valid_response(hours_offset):
    ranker = Ranker()
    result = ranker.get(timedelta(hours=hours_offset))
    assert result == TEST_TIMELINE[hours_offset]


def test__call_get_with_valid_fractional_offset__valid_response():
    ranker = Ranker()
    result = ranker.get(timedelta(seconds=1))
    assert result == TEST_TIMELINE[0]


@pytest.mark.parametrize(
    "hours_offset, error",
    [
        (-1, "Time offset cannot be negative"),
        (3, "Time offset exceeds available timeline length"),
        (4, "Time offset exceeds available timeline length"),
    ]
)
def test__call_get_with_invalid_offset__raise(hours_offset, error):
    ranker = Ranker()
    with pytest.raises(ValueError) as err:
        ranker.get(timedelta(hours=hours_offset))
    assert str(err.value) == error