import logging
from functools import lru_cache

from minio import Minio
from shoalmate.settings import get_settings, MinioSettings
from shoalmate.model import ClusterEnum


def get_cluster_settings(cluster: ClusterEnum) -> MinioSettings:
    settings = get_settings()
    cluster_to_settings = {
        ClusterEnum.CLUSTER_A: settings.cluster,  # TODO: add more clusters
    }
    return cluster_to_settings[cluster]


@lru_cache
def get_client(cluster: ClusterEnum) -> Minio:
    cluster_settings = get_cluster_settings(cluster)
    logging.info("Connect to %s", cluster)
    return Minio(
        f'{cluster_settings.host}:{cluster_settings.port}',
        access_key=cluster_settings.access_key,
        secret_key=cluster_settings.secret_key,
        secure=cluster_settings.secure,
    )


def read_green_index() -> None:
    settings = get_settings()
    client = get_client(ClusterEnum.CLUSTER_A)
    objects = client.list_objects(settings.input_bucket_index)
    logging.info("Found %d objects in bucket %s", len(list(objects)), settings.input_bucket_index)