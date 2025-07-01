from shoalmate.settings import ClusterIDEnum


def test__init_from_env__initialized(settings_mock):
    assert settings_mock.cluster_id == ClusterIDEnum.CLUSTER_A
    assert settings_mock.cluster_a.access_key == "test_access_key_a"
    assert settings_mock.cluster_a.secret_key == "test_secret_key_a"
    assert settings_mock.cluster_b.access_key == "test_access_key_b"
    assert settings_mock.cluster_b.secret_key == "test_secret_key_b"
    assert settings_mock.cluster_c.access_key == "test_access_key_c"
    assert settings_mock.cluster_c.secret_key == "test_secret_key_c"

    # Verify some default value
    assert settings_mock.cluster_a.port == 80
