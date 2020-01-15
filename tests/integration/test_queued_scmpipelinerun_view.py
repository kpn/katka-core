from uuid import UUID

import pytest


@pytest.mark.django_db
class TestSCMPipelineRunViewSet:
    def test_list_queued_pipelines(
        self, client, logged_in_user, application, queued_scm_pipeline_run, scm_releases_with_multi_pipeline_runs
    ):
        response = client.get("/queued-scm-pipeline-runs/?application=" + str(application.public_identifier))
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]["commit_hash"] == "4015B57A143AEC5156FD1444A017A32137A3FD0F"
        assert UUID(parsed[0]["application"]) == application.public_identifier
        assert len(parsed[0]["scmrelease_set"]) == 0

    def test_skipped_status_are_ignored(
        self,
        client,
        logged_in_user,
        application,
        skipped_scm_pipeline_run,
        queued_scm_pipeline_run,
        scm_releases_with_multi_pipeline_runs,
    ):
        response = client.get("/queued-scm-pipeline-runs/?application=" + str(application.public_identifier))
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]["commit_hash"] == "4015B57A143AEC5156FD1444A017A32137A3FD0F"
        assert UUID(parsed[0]["application"]) == application.public_identifier
        assert len(parsed[0]["scmrelease_set"]) == 0

    def test_list_empty_queued_pipelines(
        self, client, logged_in_user, my_other_application, scm_releases_with_multi_pipeline_runs
    ):
        response = client.get("/queued-scm-pipeline-runs/?application=" + str(my_other_application.public_identifier))
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0
