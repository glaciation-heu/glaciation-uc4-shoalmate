import pytest


@pytest.fixture
def settings_mock(mocker):
    get_settings_mock = mocker.patch('shoalmate.allocator.get_settings')
    get_settings_mock.return_value.rank_similarity_threshold = 0.1
    return get_settings_mock.return_value
