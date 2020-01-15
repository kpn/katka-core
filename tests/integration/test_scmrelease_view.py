from uuid import UUID

import pytest
from katka import models


@pytest.mark.django_db
class TestSCMReleaseViewSet:
    def test_list(self, client, logged_in_user, my_scm_pipeline_run, my_scm_release):
        response = client.get("/scm-releases/")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]["name"] == "Version 0.13.1"
        assert parsed[0]["started_at"] is None
        assert parsed[0]["ended_at"] is None
        assert parsed[0]["status"] == "in progress"
        assert len(parsed[0]["scm_pipeline_runs"]) == 1
        assert UUID(parsed[0]["scm_pipeline_runs"][0]) == my_scm_pipeline_run.public_identifier
        UUID(parsed[0]["public_identifier"])  # should not raise

    def test_filtered_list(
        self, client, logged_in_user, my_scm_pipeline_run, my_scm_release, another_scm_pipeline_run, another_scm_release
    ):

        response = client.get("/scm-releases/" f"?scm_pipeline_runs={str(another_scm_pipeline_run.public_identifier)}")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]["name"] == "Version 15.0"
        assert parsed[0]["started_at"] is None
        assert parsed[0]["ended_at"] is None
        assert parsed[0]["status"] == "in progress"
        assert len(parsed[0]["scm_pipeline_runs"]) == 1
        assert UUID(parsed[0]["scm_pipeline_runs"][0]) == another_scm_pipeline_run.public_identifier

    def test_filter_by_application(
        self,
        client,
        logged_in_user,
        my_scm_pipeline_run,
        my_scm_release,
        another_scm_pipeline_run,
        another_scm_release,
        my_other_application,
    ):
        response = client.get("/scm-releases/" f"?application={str(my_other_application.public_identifier)}")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]["name"] == "Version 15.0"
        assert parsed[0]["started_at"] is None
        assert parsed[0]["ended_at"] is None
        assert parsed[0]["status"] == "in progress"
        assert len(parsed[0]["scm_pipeline_runs"]) == 1
        assert UUID(parsed[0]["scm_pipeline_runs"][0]) == another_scm_pipeline_run.public_identifier

    def test_filter_by_pipeline_run(
        self,
        client,
        logged_in_user,
        my_scm_pipeline_run,
        my_scm_release,
        another_scm_pipeline_run,
        another_scm_release,
        my_other_application,
    ):
        response = client.get("/scm-releases/" f"?pipeline_run={str(my_scm_pipeline_run.public_identifier)}")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]["name"] == "Version 0.13.1"
        assert parsed[0]["started_at"] is None
        assert parsed[0]["ended_at"] is None
        assert parsed[0]["status"] == "in progress"
        assert len(parsed[0]["scm_pipeline_runs"]) == 1
        assert UUID(parsed[0]["scm_pipeline_runs"][0]) == my_scm_pipeline_run.public_identifier

    def test_filter_by_different_pipeline_run(
        self,
        client,
        logged_in_user,
        my_scm_pipeline_run,
        my_scm_release,
        another_scm_pipeline_run,
        another_scm_release,
        my_other_application,
    ):
        response = client.get("/scm-releases/" f"?pipeline_run={str(another_scm_pipeline_run.public_identifier)}")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]["name"] == "Version 15.0"
        assert parsed[0]["started_at"] is None
        assert parsed[0]["ended_at"] is None
        assert parsed[0]["status"] == "in progress"
        assert len(parsed[0]["scm_pipeline_runs"]) == 1
        assert UUID(parsed[0]["scm_pipeline_runs"][0]) == another_scm_pipeline_run.public_identifier

    def test_sorted_scm_releases_created_at(self, client, logged_in_user, multiple_scm_releases):
        response = client.get("/scm-releases/")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 2
        # we can only test by the name since `created_at` is not an response field
        # New was created after old in the fixtures
        assert parsed[0]["name"] == "New"
        assert parsed[1]["name"] == "Old"

    def test_filter_by_application_multiple_pipeline_runs(
        self,
        client,
        logged_in_user,
        another_scm_pipeline_run,
        another_scm_release,
        another_another_scm_pipeline_run,
        different_scm_pipeline_run,
        my_other_application,
        multiple_scm_releases,
    ):
        response = client.get("/scm-releases/" f"?application={str(my_other_application.public_identifier)}")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 3  # two extra releases from `multiple_scm_releases`
        assert parsed[0]["name"] == "New"
        assert parsed[0]["started_at"] is None
        assert parsed[0]["ended_at"] is None
        assert parsed[0]["status"] == "in progress"
        assert len(parsed[0]["scm_pipeline_runs"]) == 2
        assert UUID(parsed[0]["scm_pipeline_runs"][0]) in [
            another_scm_pipeline_run.public_identifier,
            another_another_scm_pipeline_run.public_identifier,
            different_scm_pipeline_run.public_identifier,
        ]
        assert UUID(parsed[0]["scm_pipeline_runs"][1]) in [
            another_scm_pipeline_run.public_identifier,
            another_another_scm_pipeline_run.public_identifier,
            different_scm_pipeline_run.public_identifier,
        ]

    def test_filtered_list_non_existing_pipeline_run(
        self, client, logged_in_user, my_scm_pipeline_run, my_scm_release, another_scm_pipeline_run, another_scm_release
    ):

        response = client.get("/scm-releases/?scm_pipeline_runs=12345678-1234-5678-1234-567812345678")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_list_excludes_inactive(self, client, logged_in_user, deactivated_scm_release, another_scm_release):
        response = client.get("/scm-releases/")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1

    def test_get(self, client, logged_in_user, my_scm_pipeline_run, my_scm_release):
        response = client.get(f"/scm-releases/{my_scm_release.public_identifier}/")
        assert response.status_code == 200
        parsed = response.json()
        assert parsed["name"] == "Version 0.13.1"
        assert parsed["started_at"] is None
        assert parsed["ended_at"] is None
        assert parsed["status"] == "in progress"
        assert len(parsed["scm_pipeline_runs"]) == 1
        assert UUID(parsed["scm_pipeline_runs"][0]) == my_scm_pipeline_run.public_identifier

    def test_get_with_multiple_pipeline_runs(
        self,
        client,
        logged_in_user,
        another_scm_pipeline_run,
        another_another_scm_pipeline_run,
        scm_releases_with_multi_pipeline_runs,
    ):
        response = client.get(f"/scm-releases/{scm_releases_with_multi_pipeline_runs.public_identifier}/")
        assert response.status_code == 200
        parsed = response.json()
        assert parsed["name"] == "New"
        assert parsed["started_at"] is None
        assert parsed["ended_at"] is None
        assert parsed["status"] == "in progress"
        assert len(parsed["scm_pipeline_runs"]) == 2
        assert UUID(parsed["scm_pipeline_runs"][0]) in [
            another_scm_pipeline_run.public_identifier,
            another_another_scm_pipeline_run.public_identifier,
        ]
        assert UUID(parsed["scm_pipeline_runs"][1]) in [
            another_scm_pipeline_run.public_identifier,
            another_another_scm_pipeline_run.public_identifier,
        ]

    def test_get_excludes_inactive(self, client, logged_in_user, deactivated_scm_release):
        response = client.get(f"/scm-releases/{deactivated_scm_release.public_identifier}/")
        assert response.status_code == 404

    def test_delete(self, client, logged_in_user, my_scm_release):
        response = client.delete(f"/scm-releases/{my_scm_release.public_identifier}/")
        assert response.status_code == 405

    def test_update(self, client, logged_in_user, my_scm_pipeline_run, my_scm_release):
        url = f"/scm-releases/{my_scm_release.public_identifier}/"
        data = {"name": "Version 1", "my_scm_pipeline_run": my_scm_pipeline_run.public_identifier}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 405
        p = models.SCMRelease.objects.get(pk=my_scm_release.public_identifier)
        assert p.name == "Version 0.13.1"

    def test_update_cannot_change_pipeline_run(self, client, logged_in_user, another_scm_pipeline_run, my_scm_release):
        url = f"/scm-releases/{my_scm_release.public_identifier}/"
        data = {"name": "Version pipeline run", "scm_pipeline_runs": [another_scm_pipeline_run.public_identifier]}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 405
        p = models.SCMRelease.objects.get(pk=my_scm_release.public_identifier)
        assert p.name == "Version 0.13.1"
        pipeline_runs = p.scm_pipeline_runs.all()
        assert len(pipeline_runs) == 1
        assert pipeline_runs[0].public_identifier != another_scm_pipeline_run.public_identifier

    def test_partial_update(self, client, logged_in_user, my_scm_release):
        url = f"/scm-releases/{my_scm_release.public_identifier}/"
        data = {"name": "Version B2"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 405
        p = models.SCMRelease.objects.get(pk=my_scm_release.public_identifier)
        assert p.name == "Version 0.13.1"

    def test_create(self, client, logged_in_user, my_scm_pipeline_run):
        url = f"/scm-releases/"
        data = {"name": "Version create", "scm_pipeline_runs": f"{my_scm_pipeline_run.public_identifier},"}
        response = client.post(url, data=data, content_type="application/json")
        assert response.status_code == 405
        assert not models.SCMRelease.objects.filter(name="Version create").exists()
