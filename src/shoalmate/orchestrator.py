import logging
import re
from datetime import timedelta
from io import BytesIO
from time import sleep
from minio.datatypes import Object

from shoalmate.allocator import Allocator
from shoalmate.clients.minio import get_client
from shoalmate.settings import get_settings, ClusterIDEnum


class Orchestrator:
    """Orchestrates the movement of objects between MinIO buckets across clusters."""

    _object_name_regexp = re.compile(r".*_year(\d+)_(\d+)\.parquet")
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
        time_offset = self._get_time_offset_from_name(obj.object_name)  # type: ignore[arg-type]
        target_cluster_id = self._allocator.get_target_cluster(time_offset)
        logging.info(f"Moving {obj.object_name} to cluster {target_cluster_id}")
        self._wait_if_busy(target_cluster_id)
        target_client = get_client(target_cluster_id)
        response = self._source_client.get_object(
            self._settings.input_bucket_chunks,
            obj.object_name,  # type: ignore[arg-type]
        )
        target_client.put_object(
            self._settings.output_bucket,
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
            if count > self._settings.output_bucket_capacity:
                logging.info(
                    "Wait cluster %s because it has %d unprocessed objects ",
                    target_cluster_id.value,
                    count,
                )
                sleep(self._sleep_time)
            else:
                break

    def _get_output_count(self, target_cluster_id: ClusterIDEnum) -> int:
        client = get_client(target_cluster_id)
        return len(list(client.list_objects(self._settings.output_bucket)))

    @classmethod
    def _get_time_offset_from_name(cls, object_name: str) -> timedelta:
        match = cls._object_name_regexp.fullmatch(object_name)
        _year, minutes = match.groups()  # type: ignore[union-attr]
        total_minutes = int(minutes)
        time_offset = timedelta(minutes=total_minutes)
        return time_offset
