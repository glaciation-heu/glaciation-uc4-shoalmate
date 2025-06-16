import logging
from datetime import datetime

from minio.datatypes import Object

from shoalmate.client import get_client
from shoalmate.model import ClusterEnum
from shoalmate.settings import get_settings


GreenIndex = dict[ClusterEnum, dict[datetime, float]]


class IndexStorage:

    _index: GreenIndex

    def __init__(self) -> None:
        objects = self._download()
        self._index = self._parse(objects)

    @staticmethod
    def _download() -> set[Object]:
        client = get_client(ClusterEnum.CLUSTER_A)  # TODO: support more clusters
        settings = get_settings()
        bucket = settings.input_bucket_index
        objects = client.list_objects(bucket)
        objects_set = set(objects)
        logging.info("Found %d objects in bucket %s", len(objects_set), bucket)
        return objects_set

    @staticmethod
    def _parse(objects: set[Object]) -> GreenIndex:
        index: GreenIndex = {}
        for obj in objects:
            pass
        return index

    def get_indexes(self, date: datetime) -> tuple[tuple[ClusterEnum, float]]:
        pass
