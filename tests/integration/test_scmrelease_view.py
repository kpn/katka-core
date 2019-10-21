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
                'from_hash': '4015B57A143AEC5156FD1444A017A32137A3FD0F',
                'to_hash': '0a032e92f77797d9be0ea3ad6c595392313ded72',
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
                'from_hash': '4015B57A143AEC5156FD1444A017A32137A3FD0F',
                'to_hash': '0a032e92f77797d9be0ea3ad6c595392313ded72',
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
        assert parsed[0]['released'] is None
        assert parsed[0]['from_hash'] == '577fe3f6a091aa4bad996623b1548b87f4f9c1f8'
        assert parsed[0]['to_hash'] == 'a49954f060b1b7605e972c9448a74d4067547443'
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
        assert parsed[0]['released'] is None
        assert parsed[0]['from_hash'] == '100763d7144e1f993289bd528dc698dd3906a807'
        assert parsed[0]['to_hash'] == '38d72050370e6e0b43df649c9630f7135ef6de0d'
        assert parsed[0]['status'] == 'in progress'
        assert len(parsed[0]['scm_pipeline_runs']) == 1
        assert UUID(parsed[0]['scm_pipeline_runs'][0]) == another_scm_pipeline_run.public_identifier

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
        assert parsed['released'] is None
        assert parsed['from_hash'] == '577fe3f6a091aa4bad996623b1548b87f4f9c1f8'
        assert parsed['to_hash'] == 'a49954f060b1b7605e972c9448a74d4067547443'
        assert parsed['status'] == 'in progress'
        assert len(parsed['scm_pipeline_runs']) == 1
        assert UUID(parsed['scm_pipeline_runs'][0]) == scm_pipeline_run.public_identifier

    def test_get_excludes_inactive(self, client, logged_in_user, deactivated_scm_release):
        response = client.get(f'/scm-releases/{deactivated_scm_release.public_identifier}/')
        assert response.status_code == 404

    def test_delete(self, client, logged_in_user, scm_release):
        response = client.delete(f'/scm-releases/{scm_release.public_identifier}/')
        assert response.status_code == 405

    def test_update(self, client, logged_in_user, scm_pipeline_run, scm_release):
        url = f'/scm-releases/{scm_release.public_identifier}/'
        data = {'name': 'Version 1', 'released': '2018-06-16 12:34:56',
                'from_hash': '4015B57A143AEC5156FD1444A017A32137A3FD0F',
                'to_hash': '0a032e92f77797d9be0ea3ad6c595392313ded72',
                'scm_pipeline_run': scm_pipeline_run.public_identifier}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 405
        p = models.SCMRelease.objects.get(pk=scm_release.public_identifier)
        assert p.name == 'Version 0.13.1'

    def test_update_cannot_change_hashes(self, client, logged_in_user, scm_pipeline_run, scm_release):
        url = f'/scm-releases/{scm_release.public_identifier}/'
        data = {'name': 'Version hash', 'released': '2018-06-16 12:34:56',
                'from_hash': 'BBBBB57A143AEC5156FD1444A017A32137A3FD0F',
                'to_hash': 'AAAAe92f77797d9be0ea3ad6c595392313ded72',
                'scm_pipeline_run': scm_pipeline_run.public_identifier}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 405
        p = models.SCMRelease.objects.get(pk=scm_release.public_identifier)
        assert p.from_hash != 'BBBBB57A143AEC5156FD1444A017A32137A3FD0F'
        assert p.to_hash != 'AAAAe92f77797d9be0ea3ad6c595392313ded72'

    def test_update_cannot_change_pipeline_run(self, client, logged_in_user, another_scm_pipeline_run, scm_release):
        url = f'/scm-releases/{scm_release.public_identifier}/'
        data = {'name': 'Version pipeline run', 'released': '2018-06-16 12:34:56',
                'from_hash': '577fe3f6a091aa4bad996623b1548b87f4f9c1f8',
                'to_hash': 'a49954f060b1b7605e972c9448a74d4067547443',
                'scm_pipeline_runs': [another_scm_pipeline_run.public_identifier]}
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
                'from_hash': '4015B57A143AEC5156FD1444A017A32137A3FD0F',
                'to_hash': '0a032e92f77797d9be0ea3ad6c595392313ded72',
                'scm_pipeline_runs': f'{scm_pipeline_run.public_identifier},'}
        response = client.post(url, data=data, content_type='application/json')
        assert response.status_code == 405
        assert not models.SCMRelease.objects.filter(name='Version create').exists()
