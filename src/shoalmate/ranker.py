import logging
from csv import DictReader
from datetime import timedelta
from io import StringIO
from typing import Iterator

from minio.datatypes import Object

from shoalmate.client import get_client
from shoalmate.settings import get_settings, ClusterIDEnum


Ranks = dict[ClusterIDEnum, float]
_Timeline = tuple[Ranks, ...]


class Ranker:
    """Provide Green Energy Index values for all clusters at some moment."""

    def __init__(self) -> None:
        self._timeline = _Loader().load()

    def get(self, time_offset: timedelta) -> Ranks:
        """Get the Green Energy Index for all clusters at the given time offset."""
        self._validate(time_offset)
        hours = int(time_offset.total_seconds() // 3600)
        return self._timeline[hours % len(self._timeline)]

    def _validate(self, time_offset: timedelta) -> None:
        if time_offset.total_seconds() < 0:
            raise ValueError("Time offset cannot be negative")
        elif time_offset.total_seconds() // 3600 >= len(self._timeline):
            raise ValueError("Time offset exceeds available timeline length")


class _Loader:
    """Loads Green Energy Index timeline from MinIO."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client = get_client(self._settings.cluster_id)

    def load(self) -> _Timeline:
        logging.info("Load green index dataset")
        objects = self._load_list()
        index = tuple(self._load_items(objects))
        logging.info("Loaded green index with %d entries (hourly for %d years)", len(index), len(index) / (24 * 365))
        return index

    def _load_list(self) -> tuple[Object]:
        bucket = self._settings.input_bucket_index
        objects = tuple(
            sorted(
                self._client.list_objects(bucket),
                key=lambda obj: obj.object_name
            )
        )
        logging.info("Found %d objects in bucket %s", len(objects), bucket)
        # noinspection PyTypeChecker
        return objects

    def _load_items(self, objects: tuple[Object]) -> Iterator[Ranks]:
        for object_ in objects:
            data = self._load_data(object_)
            for ranks in self._parse_data(data):
                yield ranks

    def _load_data(self, object_: Object) -> str:
        logging.info("Read /%s/%s", self._settings.input_bucket_index, object_.object_name)
        response = self._client.get_object(
            self._settings.input_bucket_index,
            object_.object_name,
        )
        return response.read().decode('utf-8')

    @staticmethod
    def _parse_data(data: str) -> Iterator[Ranks]:
        for row in DictReader(StringIO(data)):
            if int(row['TIMESTAMP']) > 365 * 24 - 1:
                break
            result = {
                ClusterIDEnum.CLUSTER_A: float(row['GI_siteA']),
                ClusterIDEnum.CLUSTER_B: float(row['GI_siteB']),
                ClusterIDEnum.CLUSTER_C: float(row['GI_siteC']),
            }
            yield result