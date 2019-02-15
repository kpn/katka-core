from uuid import UUID

import pytest
from katka import models
from katka.constants import STATUS_INACTIVE


@pytest.mark.django_db
class TestApplicationViewSetUnauthenticated:
    """
    When a user is not logged in, no group information is available, so nothing is returned.

    For listing, that would be an empty list for other operations, an error like the object could
    not be found, except on create (you need to be part of a group and anonymous users do not have any)
    """

    def test_list(self, client):
        response = client.get('/applications/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, application):
        response = client.get(f'/applications/{application.name}/')
        assert response.status_code == 404

    def test_delete(self, client, application):
        response = client.delete(f'/applications/{application.name}/')
        assert response.status_code == 404

    def test_update(self, client, project, application):
        url = f'/applications/{application.name}/'
        data = {'name': 'B-Team', 'group': 'group1', 'project': project.public_identifier}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 404

    def test_partial_update(self, client, application):
        url = f'/applications/{application.name}/'
        response = client.patch(url, {'name': 'B-Team'}, content_type='application/json')
        assert response.status_code == 404

    def test_create(self, client, project):
        url = '/applications/'
        data = {'name': 'Project D', 'slug': 'PRJD', 'project': project.public_identifier}
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 403


@pytest.mark.django_db
class TestApplicationViewSet:
    def test_list(self, client, logged_in_user, team, project, application):
        response = client.get('/applications/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]['name'] == 'Application D'
        assert parsed[0]['slug'] == 'APPD'
        parsed_project = parsed[0]['project']
        assert UUID(parsed_project) == project.public_identifier

    def test_list_excludes_inactive(self, client, logged_in_user, team, project, deactivated_application):
        response = client.get('/applications/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, logged_in_user, project, application):
        response = client.get(f'/applications/{application.public_identifier}/')
        assert response.status_code == 200
        parsed = response.json()
        assert parsed['name'] == 'Application D'
        assert parsed['slug'] == 'APPD'
        assert UUID(parsed['project']) == project.public_identifier

    def test_get_excludes_inactive(self, client, logged_in_user, team, project, deactivated_application):
        response = client.get(f'/applications/{deactivated_application.public_identifier}/')
        assert response.status_code == 404

    def test_delete(self, client, logged_in_user, team, project, application):
        response = client.delete(f'/applications/{application.public_identifier}/')
        assert response.status_code == 204
        a = models.Application.objects.get(pk=application.public_identifier)
        assert a.status == STATUS_INACTIVE

    def test_update(self, client, logged_in_user, project, application, scm_repository):
        url = f'/applications/{application.public_identifier}/'
        data = {'name': 'Application X', 'slug': 'APPX',
                'project': project.public_identifier,
                'scm_repository': scm_repository.public_identifier}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 200
        a = models.Application.objects.get(pk=application.public_identifier)
        assert a.name == 'Application X'

    def test_update_deactivated_team(self, client, logged_in_user, deactivated_project, application):
        url = f'/applications/{application.public_identifier}/'
        data = {'name': 'Application X', 'slug': 'APPX', 'project': deactivated_project.public_identifier}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 403

    def test_update_nonexistent_team(self, client, logged_in_user, application):
        url = f'/applications/{application.public_identifier}/'
        data = {'name': 'Application X', 'slug': 'APPX', 'project': '00000000-0000-0000-0000-000000000000'}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 403

    def test_partial_update(self, client, logged_in_user, application):
        url = f'/applications/{application.public_identifier}/'
        data = {'name': 'Application X'}
        response = client.patch(url, data, content_type='application/json')
        assert response.status_code == 200
        a = models.Application.objects.get(pk=application.public_identifier)
        assert a.name == 'Application X'

    def test_create(self, client, logged_in_user, project, scm_repository):
        initial_count = models.Application.objects.count()
        url = f'/applications/'
        data = {'name': 'Application X', 'slug': 'APPX',
                'project': project.public_identifier,
                'scm_repository': scm_repository.public_identifier}
        response = client.post(url, data=data, content_type='application/json')
        assert response.status_code == 201
        a = models.Application.objects.get(name='Application X')
        assert a.name == 'Application X'
        assert models.Application.objects.count() == initial_count + 1
