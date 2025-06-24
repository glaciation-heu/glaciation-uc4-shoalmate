import os
from unittest.mock import patch

from shoalmate.settings import Settings, ClusterIDEnum


def test__init_from_env__initialized():
    env_vars = {
        "SHOALMATE__CLUSTER_ID": "Cluster A",
        "SHOALMATE__CLUSTER_A__ACCESS_KEY": "test_access_key_a",
        "SHOALMATE__CLUSTER_A__SECRET_KEY": "test_secret_key_a",
        "SHOALMATE__CLUSTER_B__ACCESS_KEY": "test_access_key_b",
        "SHOALMATE__CLUSTER_B__SECRET_KEY": "test_secret_key_b",
        "SHOALMATE__CLUSTER_C__ACCESS_KEY": "test_access_key_c",
        "SHOALMATE__CLUSTER_C__SECRET_KEY": "test_secret_key_c",
    }
    with patch.dict(os.environ, env_vars, clear=True):
        settings = Settings()

        # Verify that settings were read correctly
        assert settings.cluster_id == ClusterIDEnum.CLUSTER_A
        assert settings.cluster_a.access_key == "test_access_key_a"
        assert settings.cluster_a.secret_key == "test_secret_key_a"
        assert settings.cluster_b.access_key == "test_access_key_b"
        assert settings.cluster_b.secret_key == "test_secret_key_b"
        assert settings.cluster_c.access_key == "test_access_key_c"
        assert settings.cluster_c.secret_key == "test_secret_key_c"

        # Verify some default value
        assert settings.cluster_a.port == 9000
