import logging
from datetime import timedelta
from io import BytesIO
from time import sleep
from minio.datatypes import Object

from shoalmate.clients.minio import get_client, get_cluster_settings
from shoalmate.settings import get_settings, ClusterIDEnum
from timesim.schemas import Timesim
from timesim.timesim import get_timesim_state

from shoalmate.ranker import Ranker, RankerDebugInfo
from itertools import cycle


class Orchestrator:
    """Orchestrates the movement of objects between MinIO buckets across clusters."""

    _sleep_time = 10

    def __init__(self) -> None:
        self._settings = get_settings()
        self._source_client = get_client(self._settings.cluster_id)
        self._ranker = Ranker()

    def run(self) -> None:
        while True:
            self.run_once()

    def run_once(self) -> None:
        for obj in self._list():
            self._move(obj)

    def _list(self) -> list[Object]:
        bucket = self._settings.input_bucket_chunks
        objects = list(self._source_client.list_objects(bucket))
        objects.sort(key=lambda x: x.object_name if x.object_name else "")
        return objects

    def _get_target_bucket(self, cluster_id: ClusterIDEnum) -> str:
        timesim = self._get_active_timesim_state()
        out_bucket = get_cluster_settings(cluster_id).output_bucket
        if timesim.multicluster != 0:
            out_bucket += f"-{cluster_id.lower()}"
        return out_bucket

    def _get_output_count(self, target_cluster_id: ClusterIDEnum) -> int:
        client = get_client(target_cluster_id)
        bucket = self._get_target_bucket(target_cluster_id)
        return len(list(client.list_objects(bucket)))

    def _is_busy(self, target_cluster_id: ClusterIDEnum) -> bool:
        count = self._get_output_count(target_cluster_id)
        return count > get_cluster_settings(target_cluster_id).output_bucket_capacity

    def _get_target(
        self, time_offset: timedelta
    ) -> tuple[ClusterIDEnum, str, RankerDebugInfo]:
        ranks, debug_info = self._ranker.get(time_offset)
        for cluster in cycle(
            sorted(ranks, key=lambda k: str(ranks.get(k)), reverse=True)
        ):
            if self._is_busy(cluster):
                continue
            else:
                return cluster, self._get_target_bucket(cluster), debug_info
        logging.info(
            "Broke out of the get_target loop in the Orchestrator - NOT SUPPOSED TO HAPPEN!"
        )
        cluster = max(ranks, key=lambda k: str(ranks.get(k)))
        return cluster, self._get_target_bucket(cluster), debug_info

    def _move(self, obj: Object) -> None:
        timesim = self._get_active_timesim_state()
        time_offset = timedelta(seconds=timesim.virtual_time_sec)  # type: ignore[arg-type]
        target_cluster_id, target_bucket, debug_info = self._get_target(time_offset)
        target_bucket = self._get_target_bucket(target_cluster_id)
        logging.info(
            f"Experiment {timesim.experiment_tag}. "
            f"Moving {obj.object_name} to cluster {target_cluster_id} "
            f"by Green Index line {debug_info.green_index_line_number}."
        )
        target_client = get_client(target_cluster_id)
        response = self._source_client.get_object(
            self._settings.input_bucket_chunks,
            obj.object_name,  # type: ignore[arg-type]
        )
        target_client.put_object(
            target_bucket,
            obj.object_name,  # type: ignore[arg-type]
            BytesIO(response.data),
            obj.size,  # type: ignore[arg-type]
        )
        self._source_client.remove_object(
            self._settings.input_bucket_chunks,
            obj.object_name,  # type: ignore[arg-type]
        )

    def _get_active_timesim_state(self) -> Timesim:
        """Wait until Timesim is active and return its state."""
        while True:
            state = get_timesim_state(self._settings.timesim_url)
            if state.is_active:
                break
            else:
                logging.info(
                    "Wait %s seconds because timesim is not active." % self._sleep_time
                )
                sleep(self._sleep_time)
        return state
