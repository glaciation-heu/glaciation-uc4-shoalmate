import logging
from csv import DictReader
from io import StringIO
from typing import Iterator

from minio.datatypes import Object

from shoalmate.client import get_client
from shoalmate.model import ClusterIDEnum
from shoalmate.settings import get_settings


IndexState = dict[ClusterIDEnum, float]
IndexTimeline = list[IndexState]


class IndexStorage:

    _index: IndexTimeline

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client = get_client(self._settings.cluster_id)
        self._index = self._load()

    def _load(self) -> list[IndexState]:
        index = []
        objects = self._load_list()
        for object_ in objects:
            data = self._load_data(object_)
            for line in self._parse_data(data):
                index.append(line)
        logging.info("Loaded index with %d entries", len(index))
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

    def _load_data(self, object_: Object) -> str:
        logging.info("Read /%s/%s", self._settings.input_bucket_index, object_.object_name)
        response = self._client.get_object(
            self._settings.input_bucket_index,
            object_.object_name,
        )
        return response.read().decode('utf-8')

    @staticmethod
    def _parse_data(data: str) -> Iterator[IndexState]:
        for row in DictReader(StringIO(data)):
            if int(row['TIMESTAMP']) > 365 * 24 - 1:
                break
            data = {
                ClusterIDEnum.CLUSTER_A: float(row['GI_siteA']),
                ClusterIDEnum.CLUSTER_B: float(row['GI_siteB']),
                ClusterIDEnum.CLUSTER_C: float(row['GI_siteC']),
            }
            yield data