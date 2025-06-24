from datetime import timedelta

import pytest

from shoalmate.index import Ranker
from shoalmate.settings import ClusterIDEnum


@pytest.mark.e2e
def test__init_without_mock__data_loaded():
    """
    End-to-end test.

    The test verifies GreenIndexProvider can load data without mocking.
    Requires settings.env to be loaded and a connection to MinIO.
    """
    ranker = Ranker()
    result = ranker.get(timedelta(hours=26279))
    assert result == {
        ClusterIDEnum.CLUSTER_A: 0.36607143,
        ClusterIDEnum.CLUSTER_B: 0.08333334,
        ClusterIDEnum.CLUSTER_C: 0.19345239,
    }