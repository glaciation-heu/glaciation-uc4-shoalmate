from enum import StrEnum
from functools import lru_cache

from pydantic import BaseModel, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class ClusterIDEnum(StrEnum):
    CLUSTER_A = "A"
    CLUSTER_B = "B"
    CLUSTER_C = "C"


class MinioSettings(BaseModel):
    access_key: str
    host: str = "minio.uc4-minio.svc.cluster.local"
    port: int = 80
    secret_key: str
    secure: bool = False
    output_bucket: str = "proc"
    output_bucket_capacity: int = 10


class Settings(BaseSettings):
    # Current cluster
    cluster_id: ClusterIDEnum

    # Known clusters
    cluster_a: MinioSettings
    cluster_b: MinioSettings
    cluster_c: MinioSettings

    # MinIO buckets
    input_bucket_chunks: str = "chunks"
    input_bucket_index: str = "green-index"

    # Threshold for considering ranks similar enough to prefer the current cluster
    rank_similarity_threshold: float = 0.001

    # Base URL for Time Simulator server
    timesim_url: HttpUrl = HttpUrl("http://timesim")

    # Green Energy Index dataset name prefix.
    # Use a full object name to limit loading to a single file.
    green_index_object_name_prefix: str = "GI_year0.csv"

    model_config = SettingsConfigDict(
        env_prefix="shoalmate__",
        env_nested_delimiter="__",
    )


@lru_cache
def get_settings() -> Settings:
    # noinspection PyArgumentList
    return Settings()  # type: ignore[call-arg]
