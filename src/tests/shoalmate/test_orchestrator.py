from shoalmate.client import get_client
from shoalmate.orchestrator import Orchestrator
from shoalmate.settings import ClusterIDEnum


# noinspection PyUnusedLocal
def test__run_when_no_objects__no_action(minio_mock, settings_mock, ranker_mock):
    client = get_client(ClusterIDEnum.CLUSTER_A)
    client.make_bucket(settings_mock.input_bucket_chunks)

    Orchestrator().run_once()

    assert len(list(client.list_objects(settings_mock.input_bucket_chunks))) == 0