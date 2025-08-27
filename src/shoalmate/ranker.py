import logging
from csv import DictReader
from datetime import timedelta
from io import StringIO
from typing import Iterator

from minio.datatypes import Object

from shoalmate.clients.minio import get_client
from shoalmate.settings import get_settings, ClusterIDEnum

from timesim.timesim import get_timesim_state

from random import Random


Ranks = dict[ClusterIDEnum, float]
_Timeline = tuple[Ranks, ...]


class RankerDebugInfo:
    green_index_line_number: int

    def __init__(self, value: int) -> None:
        self.green_index_line_number = value


class Ranker:
    """Provide Green Energy Index values for all clusters at some moment."""

    def __init__(self) -> None:
        self._timeline = _Loader().load()
        self._rand = Random(
            get_settings().green_index_object_name_prefix
        )  # use the green index file as seed for random

    def _do_random(self) -> bool:
        state = get_timesim_state(get_settings().timesim_url)
        assert state.scores == "green" or state.scores == "rand", (
            "ERROR: invalid choice for Cluster Scoring!"
        )
        return state.scores == "rand"

    def get(self, time_offset: timedelta) -> tuple[Ranks, RankerDebugInfo]:
        """Get the Green Energy Index for all clusters at the given time offset."""
        # Check whether we want random ranks
        self._validate(time_offset)
        hours = int(time_offset.total_seconds() // 3600)
        line_number = hours % len(self._timeline)
        if self._do_random():
            ranks = {e: self._rand.random() for e in ClusterIDEnum}
        else:
            ranks = self._timeline[line_number]
        return ranks, RankerDebugInfo(line_number)

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
        logging.info(
            "Loaded green index with %d entries (hourly for %d years)",
            len(index),
            len(index) / (24 * 365),
        )
        return index

    def _load_list(self) -> list[Object]:
        bucket = self._settings.input_bucket_index
        prefix = self._settings.green_index_object_name_prefix
        objects = list(
            sorted(
                self._client.list_objects(bucket, prefix=prefix),
                key=lambda obj: obj.object_name if obj.object_name else "",
            )
        )
        logging.info("Found %d objects in bucket %s", len(objects), bucket)
        # noinspection PyTypeChecker
        return objects

    def _load_items(self, objects: list[Object]) -> Iterator[Ranks]:
        for object_ in objects:
            data = self._load_data(object_)
            for ranks in self._parse_data(data):
                yield ranks

    def _load_data(self, object_: Object) -> str:
        logging.info(
            "Read /%s/%s", self._settings.input_bucket_index, object_.object_name
        )
        response = self._client.get_object(
            self._settings.input_bucket_index,
            object_.object_name,  # type: ignore[arg-type]
        )
        return response.read().decode("utf-8")

    @staticmethod
    def _parse_data(data: str) -> Iterator[Ranks]:
        for row in DictReader(StringIO(data)):
            if int(row["TIMESTAMP"]) > 365 * 24 - 1:
                break
            result = {
                ClusterIDEnum.CLUSTER_A: float(row["GI_siteA"]),
                ClusterIDEnum.CLUSTER_B: float(row["GI_siteB"]),
                ClusterIDEnum.CLUSTER_C: float(row["GI_siteC"]),
            }
            yield result
