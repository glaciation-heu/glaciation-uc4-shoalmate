from datetime import timedelta

import pytest

from shoalmate.ranker import Ranker
from shoalmate.settings import ClusterIDEnum


@pytest.mark.e2e
def test__init_from_remote__data_loaded() -> None:
    """
    End-to-end test.

    The test verifies GreenIndexProvider can load data without mocking.
    Requires settings.env to be loaded and a connection to MinIO.
    """
    ranker = Ranker()
    hours = 365 * 24 - 1
    ranks, debug_info = ranker.get(timedelta(hours=hours))
    assert ranks == {
        ClusterIDEnum.CLUSTER_A: 0.75,
        ClusterIDEnum.CLUSTER_B: 0.4732143,
        ClusterIDEnum.CLUSTER_C: 0.42559522,
    }
    assert debug_info.green_index_line_number == hours
