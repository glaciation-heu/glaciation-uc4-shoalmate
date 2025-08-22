import os

import pytest

from unittest.mock import Mock

from shoalmate.settings import Settings, get_settings


@pytest.fixture
def settings_mock(mocker: Mock) -> Settings:
    env_vars = {
        "SHOALMATE__CLUSTER_ID": "A",
        "SHOALMATE__CLUSTER_A__HOST": "a.example.com",
        "SHOALMATE__CLUSTER_A__ACCESS_KEY": "test_access_key_a",
        "SHOALMATE__CLUSTER_A__SECRET_KEY": "test_secret_key_a",
        "SHOALMATE__CLUSTER_B__HOST": "b.example.com",
        "SHOALMATE__CLUSTER_B__ACCESS_KEY": "test_access_key_b",
        "SHOALMATE__CLUSTER_B__SECRET_KEY": "test_secret_key_b",
        "SHOALMATE__CLUSTER_C__HOST": "c.example.com",
        "SHOALMATE__CLUSTER_C__ACCESS_KEY": "test_access_key_c",
        "SHOALMATE__CLUSTER_C__SECRET_KEY": "test_secret_key_c",
    }
    get_settings.cache_clear()
    mocker.patch.dict(os.environ, env_vars, clear=True)
    return get_settings()
