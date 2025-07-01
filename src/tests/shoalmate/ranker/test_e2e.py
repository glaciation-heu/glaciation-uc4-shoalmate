from datetime import timedelta

import pytest

from shoalmate.ranker import Ranker
from shoalmate.settings import ClusterIDEnum


@pytest.mark.e2e
def test__init_from_remote__data_loaded():
    """
    End-to-end test.

    The test verifies GreenIndexProvider can load data without mocking.
    Requires settings.env to be loaded and a connection to MinIO.
    """
    ranker = Ranker()
    result = ranker.get(timedelta(hours=365 * 24 - 1))
    assert result == {
        ClusterIDEnum.CLUSTER_A: 0.75,
        ClusterIDEnum.CLUSTER_B: 0.4732143,
        ClusterIDEnum.CLUSTER_C: 0.42559522,
    }
