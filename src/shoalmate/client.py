import logging
from functools import lru_cache

from minio import Minio

from shoalmate.settings import get_settings, MinioSettings, ClusterIDEnum


def _get_cluster_settings(cluster: ClusterIDEnum) -> MinioSettings:
    settings = get_settings()
    cluster_to_settings = {
        ClusterIDEnum.CLUSTER_A: settings.cluster_a,
        ClusterIDEnum.CLUSTER_B: settings.cluster_b,
        ClusterIDEnum.CLUSTER_C: settings.cluster_c,
    }
    return cluster_to_settings[cluster]


@lru_cache
def get_client(cluster_id: ClusterIDEnum) -> Minio:
    cluster_settings = _get_cluster_settings(cluster_id)
    logging.info("Connect to cluster %s", cluster_id)
    return Minio(
        f'{cluster_settings.host}:{cluster_settings.port}',
        access_key=cluster_settings.access_key,
        secret_key=cluster_settings.secret_key,
        secure=cluster_settings.secure,
    )