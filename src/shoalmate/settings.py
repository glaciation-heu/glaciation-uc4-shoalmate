from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class MinioSettings(BaseModel):
    access_key: str
    host: str = 'minio.uc4-minio.svc.cluster.local'
    port: int = 9000
    secret_key: str
    secure: bool = False


class Settings(BaseSettings):
    cluster: MinioSettings
    input_bucket_chunks: str = 'chunks'
    input_bucket_index: str = 'green-index'
    output_bucket: str = 'proc'

    model_config = SettingsConfigDict(
        env_prefix='shoalmate__',
        env_nested_delimiter='__',
    )


@lru_cache
def get_settings() -> Settings:
    # noinspection PyArgumentList
    return Settings()