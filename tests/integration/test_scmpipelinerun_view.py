from uuid import UUID

import pytest
from katka import models


@pytest.mark.django_db
class TestSCMPipelineRunViewSetUnauthenticated:
    """
    When a user is not logged in, no group information is available, so nothing is returned.

    For listing, that would be an empty list for other operations, an error like the object could
    not be found, except on create (you need to be part of a group and anonymous users do not have any)
    """

    def test_list(self, client, scm_pipeline_run):
        response = client.get('/scm-pipeline-runs/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, scm_pipeline_run):
        response = client.get(f'/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/')
        assert response.status_code == 404

    def test_delete(self, client, scm_pipeline_run):
        response = client.delete(f'/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/')
        assert response.status_code == 404

    def test_update(self, client, application, scm_pipeline_run):
        url = f'/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/'
        data = {'commit_hash': '0a032e92f77797d9be0ea3ad6c595392313ded72',
                'status': 'success',
                'steps_total': 10,
                'steps_completed': 5,
                'application': application.public_identifier}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 404

    def test_partial_update(self, client, scm_pipeline_run):
        url = f'/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/'
        data = {'steps_completed': 4}
        response = client.patch(url, data, content_type='application/json')
        assert response.status_code == 404

    def test_create(self, client, application, scm_pipeline_run):
        url = f'/scm-pipeline-runs/'
        data = {'commit_hash': '4015B57A143AEC5156FD1444A017A32137A3FD0F',
                'status': 'in progress',
                'steps_total': 10,
                'application': application.public_identifier}
        response = client.post(url, data=data, content_type='application/json')
        assert response.status_code == 403


@pytest.mark.django_db
class TestSCMPipelineRunViewSet:

    def test_list(self, client, logged_in_user, application, scm_pipeline_run, scm_release):
        response = client.get('/scm-pipeline-runs/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]['commit_hash'] == '4015B57A143AEC5156FD1444A017A32137A3FD0F'
        assert UUID(parsed[0]['application']) == application.public_identifier
        UUID(parsed[0]['public_identifier'])  # should not raise
        assert len(parsed[0]['scmrelease_set']) == 1

    def test_filtered_list(self, client, logged_in_user, application, scm_pipeline_run,
                           another_application, another_scm_pipeline_run, scm_release, another_scm_release):

        response = client.get('/scm-pipeline-runs/?application=' + str(another_application.public_identifier))
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]['commit_hash'] == '1234567A143AEC5156FD1444A017A3213654321'
        assert UUID(parsed[0]['application']) == another_application.public_identifier
        assert UUID(parsed[0]['public_identifier']) == another_scm_pipeline_run.public_identifier
        assert len(parsed[0]['scmrelease_set']) == 1

    def test_filtered_by_scmrelease(self, client, logged_in_user, application, scm_pipeline_run, scm_release,
                                    another_application, another_scm_pipeline_run, another_scm_release):

        response = client.get('/scm-pipeline-runs/?scmrelease=' + str(another_scm_release.public_identifier))
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]['commit_hash'] == '1234567A143AEC5156FD1444A017A3213654321'
        assert UUID(parsed[0]['application']) == another_application.public_identifier
        assert UUID(parsed[0]['public_identifier']) == another_scm_pipeline_run.public_identifier
        assert len(parsed[0]['scmrelease_set']) == 1

    def test_filtered_by_release(self, client, logged_in_user, application, scm_pipeline_run, scm_release,
                                 another_application, another_scm_pipeline_run, another_scm_release):

        response = client.get('/scm-pipeline-runs/?release=' + str(another_scm_release.public_identifier))
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]['commit_hash'] == '1234567A143AEC5156FD1444A017A3213654321'
        assert UUID(parsed[0]['application']) == another_application.public_identifier
        assert UUID(parsed[0]['public_identifier']) == another_scm_pipeline_run.public_identifier
        assert len(parsed[0]['scmrelease_set']) == 1

    def test_filtered_by_release_over_scmrelease(self, client, logged_in_user, application, scm_pipeline_run,
                                                 scm_release, another_application, another_scm_pipeline_run,
                                                 another_scm_release):
        response = client.get('/scm-pipeline-runs/?release=' + str(another_scm_release.public_identifier)
                              + '&scmrelease=dummy')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]['commit_hash'] == '1234567A143AEC5156FD1444A017A3213654321'
        assert UUID(parsed[0]['application']) == another_application.public_identifier
        assert UUID(parsed[0]['public_identifier']) == another_scm_pipeline_run.public_identifier
        assert len(parsed[0]['scmrelease_set']) == 1

    def test_filtered_list_non_existing_application(self, client, logged_in_user, application, scm_pipeline_run,
                                                    another_application, another_scm_pipeline_run):

        response = client.get('/scm-pipeline-runs/?application=12345678-1234-5678-1234-567812345678')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_list_excludes_inactive(self, client, logged_in_user, deactivated_scm_pipeline_run):
        response = client.get('/scm-pipeline-runs/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, logged_in_user, application, scm_pipeline_run):
        response = client.get(f'/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/')
        assert response.status_code == 200
        parsed = response.json()
        assert parsed['commit_hash'] == '4015B57A143AEC5156FD1444A017A32137A3FD0F'
        assert UUID(parsed['application']) == application.public_identifier
        UUID(parsed['public_identifier'])  # should not raise

    def test_get_excludes_inactive(self, client, logged_in_user, deactivated_scm_pipeline_run):
        response = client.get(f'/scm-pipeline-runs/{deactivated_scm_pipeline_run.public_identifier}/')
        assert response.status_code == 404

    def test_delete(self, client, logged_in_user, scm_pipeline_run):
        response = client.delete(f'/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/')
        assert response.status_code == 204
        p = models.SCMPipelineRun.objects.get(pk=scm_pipeline_run.public_identifier)
        assert p.deleted is True

    def test_update(self, client, logged_in_user, application, scm_pipeline_run):
        url = f'/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/'
        pipeline_yaml = '''stages:
  - release

do-release:
  stage: release
'''
        data = {'commit_hash': '0a032e92f77797d9be0ea3ad6c595392313ded72',
                'status': 'success',
                'steps_total': 10,
                'steps_completed': 5,
                'pipeline_yaml': pipeline_yaml,
                'application': application.public_identifier}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 200
        p = models.SCMPipelineRun.objects.get(pk=scm_pipeline_run.public_identifier)
        assert p.commit_hash == '0a032e92f77797d9be0ea3ad6c595392313ded72'

    def test_partial_update(self, client, logged_in_user, scm_pipeline_run):
        url = f'/scm-pipeline-runs/{scm_pipeline_run.public_identifier}/'
        data = {'steps_completed': 4}
        response = client.patch(url, data, content_type='application/json')
        assert response.status_code == 200
        p = models.SCMPipelineRun.objects.get(pk=scm_pipeline_run.public_identifier)
        assert p.steps_completed == 4

    def test_create(self, client, logged_in_user, application, scm_pipeline_run):
        initial_count = models.SCMPipelineRun.objects.count()
        url = f'/scm-pipeline-runs/'
        data = {'commit_hash': '4015B57A143AEC5156FD1444A017A32137A3FD0F',
                'application': application.public_identifier}
        response = client.post(url, data=data, content_type='application/json')
        assert response.status_code == 201
        assert models.SCMPipelineRun.objects.filter(commit_hash='4015B57A143AEC5156FD1444A017A32137A3FD0F').exists()
        assert models.SCMPipelineRun.objects.count() == initial_count + 1
