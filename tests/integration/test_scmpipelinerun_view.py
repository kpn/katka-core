from uuid import UUID

from django.db import transaction

import pytest
from katka import models
from katka.constants import PIPELINE_STATUS_FAILED, PIPELINE_STATUS_SKIPPED, PIPELINE_STATUS_SUCCESS
from katka.fields import username_on_model


@pytest.mark.django_db
class TestSCMPipelineRunViewSetUnauthenticated:
    """
    When a user is not logged in, no group information is available, so nothing is returned.

    For listing, that would be an empty list for other operations, an error like the object could
    not be found, except on create (you need to be part of a group and anonymous users do not have any)
    """

    def test_list(self, client, scm_pipeline_run):
        response = client.get("/scm-pipeline-runs/")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, scm_pipeline_run):
        response = client.get(f"/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/")
        assert response.status_code == 404

    def test_delete(self, client, scm_pipeline_run):
        response = client.delete(f"/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/")
        assert response.status_code == 404

    def test_update(self, client, application, scm_pipeline_run):
        url = f"/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/"
        data = {
            "commit_hash": "0a032e92f77797d9be0ea3ad6c595392313ded72",
            "status": "success",
            "steps_total": 10,
            "steps_completed": 5,
            "application": application.public_identifier,
        }
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 404

    def test_partial_update(self, client, scm_pipeline_run):
        url = f"/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/"
        data = {"steps_completed": 4}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 404

    def test_create(self, client, application, scm_pipeline_run):
        url = f"/scm-pipeline-runs/"
        data = {
            "commit_hash": "4015B57A143AEC5156FD1444A017A32137A3FD0F",
            "status": "in progress",
            "steps_total": 10,
            "application": application.public_identifier,
        }
        response = client.post(url, data=data, content_type="application/json")
        assert response.status_code == 403


@pytest.mark.django_db
class TestSCMPipelineRunViewSet:
    def test_list(self, client, logged_in_user, application, scm_pipeline_run, scm_release):
        response = client.get("/scm-pipeline-runs/")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]["commit_hash"] == "4015B57A143AEC5156FD1444A017A32137A3FD0F"
        assert UUID(parsed[0]["application"]) == application.public_identifier
        UUID(parsed[0]["public_identifier"])  # should not raise
        assert len(parsed[0]["scmrelease_set"]) == 1

    def test_filtered_list(
        self,
        client,
        logged_in_user,
        application,
        scm_pipeline_run,
        another_application,
        another_scm_pipeline_run,
        scm_release,
        another_scm_release,
    ):

        response = client.get("/scm-pipeline-runs/?application=" + str(another_application.public_identifier))
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]["commit_hash"] == "1234567A143AEC5156FD1444A017A3213654321"
        assert UUID(parsed[0]["application"]) == another_application.public_identifier
        assert UUID(parsed[0]["public_identifier"]) == another_scm_pipeline_run.public_identifier
        assert len(parsed[0]["scmrelease_set"]) == 1

    def test_filtered_by_scmrelease(
        self,
        client,
        logged_in_user,
        application,
        scm_pipeline_run,
        scm_release,
        another_application,
        another_scm_pipeline_run,
        another_scm_release,
    ):

        response = client.get("/scm-pipeline-runs/?scmrelease=" + str(another_scm_release.public_identifier))
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]["commit_hash"] == "1234567A143AEC5156FD1444A017A3213654321"
        assert UUID(parsed[0]["application"]) == another_application.public_identifier
        assert UUID(parsed[0]["public_identifier"]) == another_scm_pipeline_run.public_identifier
        assert len(parsed[0]["scmrelease_set"]) == 1

    def test_filtered_by_release(
        self,
        client,
        logged_in_user,
        application,
        scm_pipeline_run,
        scm_release,
        another_application,
        another_scm_pipeline_run,
        another_scm_release,
        another_another_scm_pipeline_run,
    ):

        response = client.get("/scm-pipeline-runs/?release=" + str(another_scm_release.public_identifier))
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 2
        assert parsed[0]["commit_hash"] == another_another_scm_pipeline_run.commit_hash
        assert parsed[1]["commit_hash"] == another_scm_pipeline_run.commit_hash
        assert UUID(parsed[1]["application"]) == another_application.public_identifier
        assert UUID(parsed[1]["public_identifier"]) == another_scm_pipeline_run.public_identifier
        assert len(parsed[1]["scmrelease_set"]) == 1

    def test_filtered_by_release_over_scmrelease(
        self,
        client,
        logged_in_user,
        application,
        scm_pipeline_run,
        scm_release,
        another_application,
        another_scm_pipeline_run,
        another_scm_release,
    ):
        response = client.get(
            "/scm-pipeline-runs/?release=" + str(another_scm_release.public_identifier) + "&scmrelease=dummy"
        )
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]["commit_hash"] == "1234567A143AEC5156FD1444A017A3213654321"
        assert UUID(parsed[0]["application"]) == another_application.public_identifier
        assert UUID(parsed[0]["public_identifier"]) == another_scm_pipeline_run.public_identifier
        assert len(parsed[0]["scmrelease_set"]) == 1

    def test_filtered_list_non_existing_application(
        self, client, logged_in_user, application, scm_pipeline_run, another_application, another_scm_pipeline_run
    ):

        response = client.get("/scm-pipeline-runs/?application=12345678-1234-5678-1234-567812345678")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_list_excludes_inactive(self, client, logged_in_user, deactivated_scm_pipeline_run):
        response = client.get("/scm-pipeline-runs/")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, logged_in_user, application, scm_pipeline_run):
        response = client.get(f"/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/")
        assert response.status_code == 200
        parsed = response.json()
        assert parsed["commit_hash"] == "4015B57A143AEC5156FD1444A017A32137A3FD0F"
        assert UUID(parsed["application"]) == application.public_identifier
        UUID(parsed["public_identifier"])  # should not raise

    def test_get_excludes_inactive(self, client, logged_in_user, deactivated_scm_pipeline_run):
        response = client.get(f"/scm-pipeline-runs/{deactivated_scm_pipeline_run.public_identifier}/")
        assert response.status_code == 404

    def test_delete(self, client, logged_in_user, scm_pipeline_run):
        response = client.delete(f"/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/")
        assert response.status_code == 204
        p = models.SCMPipelineRun.objects.get(pk=scm_pipeline_run.public_identifier)
        assert p.deleted is True

    def test_update(self, client, logged_in_user, application, scm_pipeline_run):
        url = f"/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/"
        pipeline_yaml = """stages:
  - release

do-release:
  stage: release
"""
        data = {
            "commit_hash": "0a032e92f77797d9be0ea3ad6c595392313ded72",
            "status": "success",
            "steps_total": 10,
            "steps_completed": 5,
            "pipeline_yaml": pipeline_yaml,
            "application": application.public_identifier,
        }
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 200
        p = models.SCMPipelineRun.objects.get(pk=scm_pipeline_run.public_identifier)
        assert p.commit_hash == "0a032e92f77797d9be0ea3ad6c595392313ded72"

    def test_partial_update(self, client, logged_in_user, scm_pipeline_run):
        url = f"/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/"
        data = {"steps_completed": 4}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 200
        p = models.SCMPipelineRun.objects.get(pk=scm_pipeline_run.public_identifier)
        assert p.steps_completed == 4

    def test_create_already_exists(self, client, logged_in_user, application, scm_pipeline_run):
        initial_count = models.SCMPipelineRun.objects.count()
        url = f"/scm-pipeline-runs/"
        # Provide a different status, should not create a new PLR
        data = {
            "commit_hash": scm_pipeline_run.commit_hash,
            "application": application.public_identifier,
            "status": "skipped",
        }

        #  This atomic transaction context allows us to do a count query after the request
        with transaction.atomic():
            response = client.post(url, data=data, content_type="application/json")

        assert response.status_code == 409
        error = response.json()
        assert error["code"] == "already_exists"
        assert models.SCMPipelineRun.objects.count() == initial_count

    def test_create_first_commit(self, client, logged_in_user, application, scm_pipeline_run):
        initial_count = models.SCMPipelineRun.objects.count()
        url = f"/scm-pipeline-runs/"
        data = {"commit_hash": "874AE57A143AEC5156FD1444A017A32137A3E34A", "application": application.public_identifier}
        response = client.post(url, data=data, content_type="application/json")
        assert response.status_code == 201
        assert models.SCMPipelineRun.objects.count() == initial_count + 1
        new_plr = models.SCMPipelineRun.objects.filter(commit_hash="874AE57A143AEC5156FD1444A017A32137A3E34A").first()
        assert new_plr.first_parent_hash is None

    def test_create_next_commit(self, client, logged_in_user, application, scm_pipeline_run):
        initial_count = models.SCMPipelineRun.objects.count()
        url = f"/scm-pipeline-runs/"
        data = {
            "commit_hash": "874AE57A143AEC5156FD1444A017A32137A3E34A",
            "first_parent_hash": "4015B57A143AEC5156FD1444A017A32137A3FD0F",
            "application": application.public_identifier,
        }
        response = client.post(url, data=data, content_type="application/json")
        assert response.status_code == 201
        assert models.SCMPipelineRun.objects.count() == initial_count + 1
        new_plr = models.SCMPipelineRun.objects.filter(commit_hash="874AE57A143AEC5156FD1444A017A32137A3E34A").first()
        assert new_plr.first_parent_hash == "4015B57A143AEC5156FD1444A017A32137A3FD0F"

    def test_create_parent_commit_not_found(self, client, logged_in_user, application, scm_pipeline_run):
        initial_count = models.SCMPipelineRun.objects.count()
        url = f"/scm-pipeline-runs/"
        data = {
            "commit_hash": "874AE57A143AEC5156FD1444A017A32137A3E34A",
            "first_parent_hash": "4015B57A143AEC5156FD1444A017A32137A3FD0G",
            "application": application.public_identifier,
        }
        response = client.post(url, data=data, content_type="application/json")
        assert response.status_code == 409
        error = response.json()
        assert error["code"] == "parent_commit_missing"
        assert models.SCMPipelineRun.objects.count() == initial_count
        assert not models.SCMPipelineRun.objects.filter(commit_hash="874AE57A143AEC5156FD1444A017A32137A3E34A").exists()


@pytest.mark.django_db
class TestSCMPipelineRunQueueOrRun:
    """
    To make sure we process pipelines in order, we put pipeline runs in progress only when previous pipeline runs
    have been completed (or skipped). These tests should verify that that functionality works correctly.
    """

    def test_first_commit(self, client, logged_in_user, application, scm_pipeline_run):
        """There is no first parent commit hash, so we can change the status to in progress"""

        url = f"/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/"
        data = {"status": "in progress"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 200
        p = models.SCMPipelineRun.objects.get(pk=scm_pipeline_run.public_identifier)
        assert p.status == "in progress"

    def test_linked_to_non_final(self, client, logged_in_user, application, scm_pipeline_run, next_scm_pipeline_run):
        """First parent is linked, but its status is not a final state"""

        url = f"/scm-pipeline-runs/{next_scm_pipeline_run.public_identifier}/"
        data = {"status": "in progress"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 200
        p = models.SCMPipelineRun.objects.get(pk=next_scm_pipeline_run.public_identifier)
        assert p.status == "queued"

    def test_not_linked_at_all(
        self, client, logged_in_user, application, scm_pipeline_run, another_another_scm_pipeline_run, caplog
    ):
        """
        The first parent points to a commit that is not present, so a sync is necessary.
        This pipeline run should be queued
        """

        url = f"/scm-pipeline-runs/{another_another_scm_pipeline_run.public_identifier}/"
        data = {"status": "in progress"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 200
        p = models.SCMPipelineRun.objects.get(pk=another_another_scm_pipeline_run.public_identifier)
        assert p.status == "queued"
        assert str(another_another_scm_pipeline_run.public_identifier) in caplog.messages[0]
        assert str(another_another_scm_pipeline_run.first_parent_hash) in caplog.messages[0]

    @pytest.mark.parametrize("status", [PIPELINE_STATUS_FAILED, PIPELINE_STATUS_SUCCESS, PIPELINE_STATUS_SKIPPED])
    def test_linked_to_final_state(
        self, status, client, logged_in_user, application, scm_pipeline_run, next_scm_pipeline_run
    ):
        """First parent is linked, and its status is in a final state"""

        scm_pipeline_run.status = status
        with username_on_model(models.SCMPipelineRun, "test"):
            scm_pipeline_run.save()

        url = f"/scm-pipeline-runs/{next_scm_pipeline_run.public_identifier}/"
        data = {"status": "in progress"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 200
        p = models.SCMPipelineRun.objects.get(pk=next_scm_pipeline_run.public_identifier)
        assert p.status == "in progress"


@pytest.mark.django_db
class TestSCMPipelineRunRunNextPipeline:
    """
    To make sure we process pipelines in order, the next pipeline should be run if it's queued.
    """

    def test_still_initializing(
        self, client, logged_in_user, application, scm_pipeline_run, next_scm_pipeline_run, caplog
    ):
        url = f"/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/"
        data = {"status": "success"}
        assert next_scm_pipeline_run.status == "initializing"
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 200
        p = models.SCMPipelineRun.objects.get(pk=next_scm_pipeline_run.public_identifier)
        assert p.status == "initializing"
        assert caplog.messages == []

    def test_non_queued(self, client, logged_in_user, application, scm_pipeline_run, next_scm_pipeline_run, caplog):
        url = f"/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/"
        data = {"status": "success"}
        with username_on_model(models.SCMPipelineRun, "test"):
            next_scm_pipeline_run.status = "in progress"
            next_scm_pipeline_run.save()

        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 200
        p = models.SCMPipelineRun.objects.get(pk=next_scm_pipeline_run.public_identifier)
        assert p.status == "in progress"
        assert caplog.messages[0] == (
            f"Next pipeline {next_scm_pipeline_run.pk} is not queued, " 'it has status "in progress", not updating'
        )

    def test_queued(self, client, logged_in_user, application, scm_pipeline_run, next_scm_pipeline_run, caplog):
        url = f"/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/"
        data = {"status": "success"}
        with username_on_model(models.SCMPipelineRun, "test"):
            next_scm_pipeline_run.status = "queued"
            next_scm_pipeline_run.save()

        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 200
        p = models.SCMPipelineRun.objects.get(pk=next_scm_pipeline_run.public_identifier)
        assert p.status == "in progress"
        assert caplog.messages == []

    def test_final_commit(self, client, logged_in_user, application, scm_pipeline_run, caplog):
        url = f"/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/"
        data = {"status": "success"}

        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 200
        assert caplog.messages == []
