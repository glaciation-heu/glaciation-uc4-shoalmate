from datetime import timedelta

from shoalmate.ranker import Ranker, RankerDebugInfo
from shoalmate.settings import get_settings, ClusterIDEnum


class Allocator:
    """Allocates target cluster based on cluster ranks."""

    def __init__(self) -> None:
        self._ranker = Ranker()
        self._settings = get_settings()

    def get_target_cluster(
        self, time_offset: timedelta
    ) -> tuple[ClusterIDEnum, RankerDebugInfo]:
        ranks, debug_info = self._ranker.get(time_offset)
        cluster_id = max(ranks, key=ranks.get)  # type: ignore[arg-type]
        threshold = self._settings.rank_similarity_threshold
        current_cluster_id = self._settings.cluster_id
        if (ranks[cluster_id] - ranks[current_cluster_id]) <= threshold:
            cluster_id = current_cluster_id
        return cluster_id, debug_info
