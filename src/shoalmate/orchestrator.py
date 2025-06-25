import logging
import re
from datetime import timedelta
from io import BytesIO
from time import sleep
from typing import Iterator
from minio.datatypes import Object

from shoalmate.allocator import Allocator
from shoalmate.client import get_client
from shoalmate.settings import get_settings


SLEEP_TIME = 3


class Orchestrator:
    """Orchestrates the movement of objects between MinIO buckets across clusters."""

    _object_name_regexp = re.compile(r".*_year(\d+)_(\d+)\.parquet")

    def __init__(self) -> None:
        self._allocator = Allocator()
        self._settings = get_settings()
        self._source_client = get_client(self._settings.cluster_id)

    def run(self) -> None:
        for obj in self._listen():
            self._move(obj)
            sleep(SLEEP_TIME)  # TODO: Replace with message listening and back pressure

    def _listen(self) -> Iterator[Object]:
        while True:
            bucket = self._settings.input_bucket_chunks
            objects = list(self._source_client.list_objects(bucket))
            objects.sort(key=lambda x: x.object_name)
            for obj in objects:
                yield obj

    def _move(self, obj: Object) -> None:
        time_offset = self._get_time_offset_from_name(obj.object_name)
        target_cluster_id = self._allocator.get_target_cluster(time_offset)
        logging.info(f"Moving {obj.object_name} to cluster {target_cluster_id}")
        target_client = get_client(target_cluster_id)
        response = self._source_client.get_object(
            self._settings.input_bucket_chunks,
            obj.object_name
        )
        target_client.put_object(
            self._settings.output_bucket,
            obj.object_name,
            BytesIO(response.data),
            obj.size
        )
        self._source_client.remove_object(
            self._settings.input_bucket_chunks,
            obj.object_name
        )

    @classmethod
    def _get_time_offset_from_name(cls, object_name: str) -> timedelta:
        match = cls._object_name_regexp.fullmatch(object_name)
        year, minutes = match.groups()
        total_minutes = int(year) * 365 * 24 * 60 + int(minutes)
        return timedelta(minutes=total_minutes)
