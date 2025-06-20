import logging
from csv import DictReader
from datetime import datetime
from io import StringIO
from typing import Iterator

from minio.datatypes import Object

from shoalmate.client import get_client
from shoalmate.model import ClusterEnum
from shoalmate.settings import get_settings


IndexState = dict[ClusterEnum, float]
IndexTimeline = list[IndexState]


class IndexStorage:

    _index: IndexTimeline

    def __init__(self) -> None:
        self._index = []
        objects = self._load_list()
        for line in self._parse_object(objects):
            self._index.append(line)
        logging.info("Index loaded with %d entries", len(self._index))

    @staticmethod
    def _load_list() -> tuple[Object]:
        client = get_client(ClusterEnum.CLUSTER_A)  # TODO: support more clusters
        settings = get_settings()
        bucket = settings.input_bucket_index
        objects = tuple(
            sorted(
                client.list_objects(bucket),
                key=lambda obj: obj.object_name
            )
        )
        logging.info("Found %d objects in bucket %s", len(objects), bucket)
        return objects

    @staticmethod
    def _parse_object(objects: tuple[Object]) -> Iterator[IndexState]:
        client = get_client(ClusterEnum.CLUSTER_A)
        settings = get_settings()
        for object_ in objects:
            logging.info("Read /%s/%s", settings.input_bucket_index, object_.object_name)
            response = client.get_object(settings.input_bucket_index, object_.object_name)
            data = response.read().decode('utf-8')
            for row in DictReader(StringIO(data)):
                if int(row['TIMESTAMP']) > 365 * 24 - 1:
                    break
                data = {
                    ClusterEnum.CLUSTER_A: float(row['GI_siteA']),
                    ClusterEnum.CLUSTER_B: float(row['GI_siteB']),
                    ClusterEnum.CLUSTER_C: float(row['GI_siteC']),
                }
                yield data