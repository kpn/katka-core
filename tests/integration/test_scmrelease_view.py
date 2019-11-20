from uuid import UUID

import pytest
from katka import models


@pytest.mark.django_db
class TestSCMReleaseViewSetUnauthenticated:
    """
    When a user is not logged in, no group information is available, so nothing is returned.

    For listing, that would be an empty list for other operations, an error like the object could
    not be found, except on create (you need to be part of a group and anonymous users do not have any)
    """

    def test_list(self, client, scm_release):
        response = client.get('/scm-releases/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, scm_release):
        response = client.get(f'/scm-releases/{scm_release.public_identifier}/')
        assert response.status_code == 404

    def test_delete(self, client, scm_release):
        response = client.delete(f'/scm-releases/{scm_release.public_identifier}/')
        assert response.status_code == 405

    def test_update(self, client, scm_pipeline_run, scm_release):
        url = f'/scm-releases/{scm_release.public_identifier}/'
        data = {'name': 'Version 1', 'released': '2018-06-16 12:34:56',
                'scm_pipeline_run': scm_pipeline_run.public_identifier}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 405

    def test_partial_update(self, client, scm_release):
        url = f'/scm-releases/{scm_release.public_identifier}/'
        data = {'name': 'v15.1'}
        response = client.patch(url, data, content_type='application/json')
        assert response.status_code == 405

    def test_create(self, client, scm_pipeline_run, scm_release):
        url = f'/scm-releases/'
        data = {'name': 'Version 1',
                'scm_pipeline_runs': [scm_pipeline_run.public_identifier]}
        response = client.post(url, data=data, content_type='application/json')
        assert response.status_code == 405


@pytest.mark.django_db
class TestSCMReleaseViewSet:

    def test_list(self, client, logged_in_user, scm_pipeline_run, scm_release):
        response = client.get('/scm-releases/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]['name'] == 'Version 0.13.1'
        assert parsed[0]['started_at'] is None
        assert parsed[0]['ended_at'] is None
        assert parsed[0]['status'] == 'in progress'
        assert len(parsed[0]['scm_pipeline_runs']) == 1
        assert UUID(parsed[0]['scm_pipeline_runs'][0]) == scm_pipeline_run.public_identifier
        UUID(parsed[0]['public_identifier'])  # should not raise

    def test_filtered_list(self, client, logged_in_user, scm_pipeline_run, scm_release, another_scm_pipeline_run,
                           another_scm_release):

        response = client.get('/scm-releases/'
                              f'?scm_pipeline_runs={str(another_scm_pipeline_run.public_identifier)}')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]['name'] == 'Version 15.0'
        assert parsed[0]['started_at'] is None
        assert parsed[0]['ended_at'] is None
        assert parsed[0]['status'] == 'in progress'
        assert len(parsed[0]['scm_pipeline_runs']) == 1
        assert UUID(parsed[0]['scm_pipeline_runs'][0]) == another_scm_pipeline_run.public_identifier

    def test_filter_by_application(self, client, logged_in_user, scm_pipeline_run, scm_release,
                                   another_scm_pipeline_run, another_scm_release, another_application):
        response = client.get('/scm-releases/'
                              f'?application={str(another_application.public_identifier)}')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]['name'] == 'Version 15.0'
        assert parsed[0]['started_at'] is None
        assert parsed[0]['ended_at'] is None
        assert parsed[0]['status'] == 'in progress'
        assert len(parsed[0]['scm_pipeline_runs']) == 1
        assert UUID(parsed[0]['scm_pipeline_runs'][0]) == another_scm_pipeline_run.public_identifier

    def test_sorted_scm_releases_created_at(self, client, logged_in_user, scm_pipeline_run, scm_release,
                                            another_scm_pipeline_run, another_scm_release,
                                            another_another_scm_pipeline_run):
        response = client.get('/scm-releases/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 2
        # we can only test by the name since `created_at` is not an response field
        # it is assumed that Version 15.0 is created after Version 0.13.1 in the fixtures
        assert parsed[0]['name'] == 'Version 15.0'
        assert parsed[1]['name'] == 'Version 0.13.1'
        assert parsed[0]['scm_pipeline_runs'][0] == str(another_another_scm_pipeline_run.public_identifier)
        assert parsed[0]['scm_pipeline_runs'][1] == str(another_scm_pipeline_run.public_identifier)

    def test_filter_by_application_multiple_pipeline_runs(self, client, logged_in_user, scm_pipeline_run, scm_release,
                                                          another_scm_pipeline_run, another_scm_release,
                                                          another_another_scm_pipeline_run, another_application):
        response = client.get('/scm-releases/'
                              f'?application={str(another_application.public_identifier)}')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]['name'] == 'Version 15.0'
        assert parsed[0]['started_at'] is None
        assert parsed[0]['ended_at'] is None
        assert parsed[0]['status'] == 'in progress'
        assert len(parsed[0]['scm_pipeline_runs']) == 2
        assert UUID(parsed[0]['scm_pipeline_runs'][0]) in [another_scm_pipeline_run.public_identifier,
                                                           another_another_scm_pipeline_run.public_identifier]
        assert UUID(parsed[0]['scm_pipeline_runs'][1]) in [another_scm_pipeline_run.public_identifier,
                                                           another_another_scm_pipeline_run.public_identifier]

    def test_filtered_list_non_existing_pipeline_run(self, client, logged_in_user, scm_pipeline_run, scm_release,
                                                     another_scm_pipeline_run, another_scm_release):

        response = client.get('/scm-releases/?scm_pipeline_runs=12345678-1234-5678-1234-567812345678')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_list_excludes_inactive(self, client, logged_in_user, deactivated_scm_release):
        response = client.get('/scm-releases/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, logged_in_user, scm_pipeline_run, scm_release):
        response = client.get(f'/scm-releases/{scm_release.public_identifier}/')
        assert response.status_code == 200
        parsed = response.json()
        assert parsed['name'] == 'Version 0.13.1'
        assert parsed['started_at'] is None
        assert parsed['ended_at'] is None
        assert parsed['status'] == 'in progress'
        assert len(parsed['scm_pipeline_runs']) == 1
        assert UUID(parsed['scm_pipeline_runs'][0]) == scm_pipeline_run.public_identifier

    def test_get_with_multiple_pipeline_runs(self, client, logged_in_user, another_scm_pipeline_run,
                                             another_another_scm_pipeline_run, another_scm_release):
        response = client.get(f'/scm-releases/{another_scm_release.public_identifier}/')
        assert response.status_code == 200
        parsed = response.json()
        assert parsed['name'] == 'Version 15.0'
        assert parsed['started_at'] is None
        assert parsed['ended_at'] is None
        assert parsed['status'] == 'in progress'
        assert len(parsed['scm_pipeline_runs']) == 2
        assert UUID(parsed['scm_pipeline_runs'][0]) in [another_scm_pipeline_run.public_identifier,
                                                        another_another_scm_pipeline_run.public_identifier]
        assert UUID(parsed['scm_pipeline_runs'][1]) in [another_scm_pipeline_run.public_identifier,
                                                        another_another_scm_pipeline_run.public_identifier]

    def test_get_excludes_inactive(self, client, logged_in_user, deactivated_scm_release):
        response = client.get(f'/scm-releases/{deactivated_scm_release.public_identifier}/')
        assert response.status_code == 404

    def test_delete(self, client, logged_in_user, scm_release):
        response = client.delete(f'/scm-releases/{scm_release.public_identifier}/')
        assert response.status_code == 405

    def test_update(self, client, logged_in_user, scm_pipeline_run, scm_release):
        url = f'/scm-releases/{scm_release.public_identifier}/'
        data = {'name': 'Version 1', 'scm_pipeline_run': scm_pipeline_run.public_identifier}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 405
        p = models.SCMRelease.objects.get(pk=scm_release.public_identifier)
        assert p.name == 'Version 0.13.1'

    def test_update_cannot_change_pipeline_run(self, client, logged_in_user, another_scm_pipeline_run, scm_release):
        url = f'/scm-releases/{scm_release.public_identifier}/'
        data = {'name': 'Version pipeline run', 'scm_pipeline_runs': [another_scm_pipeline_run.public_identifier]}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 405
        p = models.SCMRelease.objects.get(pk=scm_release.public_identifier)
        assert p.name == 'Version 0.13.1'
        pipeline_runs = p.scm_pipeline_runs.all()
        assert len(pipeline_runs) == 1
        assert pipeline_runs[0].public_identifier != another_scm_pipeline_run.public_identifier

    def test_partial_update(self, client, logged_in_user, scm_release):
        url = f'/scm-releases/{scm_release.public_identifier}/'
        data = {'name': 'Version B2'}
        response = client.patch(url, data, content_type='application/json')
        assert response.status_code == 405
        p = models.SCMRelease.objects.get(pk=scm_release.public_identifier)
        assert p.name == 'Version 0.13.1'

    def test_create(self, client, logged_in_user, scm_pipeline_run):
        url = f'/scm-releases/'
        data = {'name': 'Version create',
                'scm_pipeline_runs': f'{scm_pipeline_run.public_identifier},'}
        response = client.post(url, data=data, content_type='application/json')
        assert response.status_code == 405
        assert not models.SCMRelease.objects.filter(name='Version create').exists()
