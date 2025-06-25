from shoalmate.orchestrator import Orchestrator


def test__run_when_no_objects__no_action(minio_mock, settings_mock, ranker_mock):
    Orchestrator()