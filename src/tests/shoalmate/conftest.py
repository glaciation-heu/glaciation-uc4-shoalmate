import os

import pytest

from shoalmate.settings import Settings, get_settings


@pytest.fixture
def settings_mock(mocker) -> Settings:
    env_vars = {
        "SHOALMATE__CLUSTER_ID": "A",
        "SHOALMATE__CLUSTER_A__ACCESS_KEY": "test_access_key_a",
        "SHOALMATE__CLUSTER_A__SECRET_KEY": "test_secret_key_a",
        "SHOALMATE__CLUSTER_B__ACCESS_KEY": "test_access_key_b",
        "SHOALMATE__CLUSTER_B__SECRET_KEY": "test_secret_key_b",
        "SHOALMATE__CLUSTER_C__ACCESS_KEY": "test_access_key_c",
        "SHOALMATE__CLUSTER_C__SECRET_KEY": "test_secret_key_c",
    }
    mocker.patch.dict(os.environ, env_vars, clear=True)
    settings = Settings()

    # If the test changes Settings objects, it is consistent across the test
    mocker.patch('shoalmate.allocator.get_settings', return_value=settings)

    return settings


@pytest.fixture
def ranker_mock(mocker):
    ranker_mock = mocker.patch('shoalmate.allocator.Ranker')
    return ranker_mock.return_value