import logging
from datetime import timedelta
from io import BytesIO
from time import sleep
from minio.datatypes import Object

from shoalmate.allocator import Allocator
from shoalmate.clients.minio import get_client, get_cluster_settings
from shoalmate.settings import get_settings, ClusterIDEnum
from timesim.schemas import Timesim
from timesim.timesim import get_timesim_state


class Orchestrator:
    """Orchestrates the movement of objects between MinIO buckets across clusters."""

    _sleep_time = 10

    def __init__(self) -> None:
        self._allocator = Allocator()
        self._settings = get_settings()
        self._source_client = get_client(self._settings.cluster_id)

    def run(self) -> None:
        while True:
            self.run_once()

    def run_once(self) -> None:
        for obj in self._list():
            self._move(obj)

    def _list(self) -> list[Object]:
        bucket = self._settings.input_bucket_chunks
        objects = list(self._source_client.list_objects(bucket))
        objects.sort(key=lambda x: x.object_name)
        return objects

    def _move(self, obj: Object) -> None:
        timesim = self._get_active_timesim_state()
        time_offset = timedelta(seconds=timesim.virtual_time_sec)  # type: ignore[arg-type]
        target_cluster_id, debug_info = self._allocator.get_target_cluster(time_offset)
        logging.info(
            f"Experiment {timesim.experiment_tag}. "
            f"Moving {obj.object_name} to cluster {target_cluster_id} "
            f"by Green Index line {debug_info.green_index_line_number}."
        )
        self._wait_if_busy(target_cluster_id)
        target_client = get_client(target_cluster_id)
        response = self._source_client.get_object(
            self._settings.input_bucket_chunks,
            obj.object_name,  # type: ignore[arg-type]
        )
        target_client.put_object(
            get_cluster_settings(target_cluster_id).output_bucket,
            obj.object_name,  # type: ignore[arg-type]
            BytesIO(response.data),
            obj.size,  # type: ignore[arg-type]
        )
        self._source_client.remove_object(
            self._settings.input_bucket_chunks,
            obj.object_name,  # type: ignore[arg-type]
        )

    def _wait_if_busy(self, target_cluster_id: ClusterIDEnum) -> None:
        while True:
            count = self._get_output_count(target_cluster_id)
            if count > get_cluster_settings(target_cluster_id).output_bucket_capacity:
                logging.info(
                    "Wait cluster %s because it has %d unprocessed objects ",
                    target_cluster_id.value,
                    count,
                )
                sleep(self._sleep_time)
            else:
                break

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

    def _get_output_count(self, target_cluster_id: ClusterIDEnum) -> int:
        client = get_client(target_cluster_id)
        return len(list(client.list_objects(get_cluster_settings(target_cluster_id).output_bucket)))
