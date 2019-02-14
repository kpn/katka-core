from uuid import UUID

import pytest
from katka import models
from katka.constants import STATUS_INACTIVE


@pytest.mark.django_db
class TestProjectViewSetUnauthenticated:
    """
    When a user is not logged in, no group information is available, so nothing is returned.

    For listing, that would be an empty list for other operations, an error like the object could
    not be found, except on create (you need to be part of a group and anonymous users do not have any)
    """

    def test_list(self, client):
        response = client.get('/projects/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, project):
        response = client.get(f'/projects/{project.name}/')
        assert response.status_code == 404

    def test_delete(self, client, project):
        response = client.delete(f'/projects/{project.name}/')
        assert response.status_code == 404

    def test_update(self, client, team, project):
        url = f'/projects/{project.name}/'
        data = {'name': 'B-Team', 'group': 'group1', 'team': team.public_identifier}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 404

    def test_partial_update(self, client, project):
        url = f'/projects/{project.name}/'
        response = client.patch(url, {'name': 'B-Team'}, content_type='application/json')
        assert response.status_code == 404

    def test_create(self, client, team):
        url = '/projects/'
        data = {'name': 'Project D', 'slug': 'PRJD', 'team': team.public_identifier}
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 403


@pytest.mark.django_db
class TestProjectViewSet:
    def test_list(self, client, logged_in_user, team, project):
        response = client.get('/projects/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]['name'] == 'Project D'
        assert parsed[0]['slug'] == 'PRJD'
        parsed_team = parsed[0]['team']
        assert UUID(parsed_team) == team.public_identifier

    def test_list_excludes_inactive(self, client, logged_in_user, team, deactivated_project):
        response = client.get('/projects/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, logged_in_user, team, project):
        response = client.get(f'/projects/{project.public_identifier}/')
        assert response.status_code == 200
        parsed = response.json()
        assert parsed['name'] == 'Project D'
        assert parsed['slug'] == 'PRJD'
        assert UUID(parsed['team']) == team.public_identifier

    def test_get_excludes_inactive(self, client, logged_in_user, team, deactivated_project):
        response = client.get(f'/projects/{deactivated_project.public_identifier}/')
        assert response.status_code == 404

    def test_delete(self, client, logged_in_user, team, project):
        response = client.delete(f'/projects/{project.public_identifier}/')
        assert response.status_code == 204
        p = models.Project.objects.get(pk=project.public_identifier)
        assert p.status == STATUS_INACTIVE

    def test_update(self, client, logged_in_user, team, project):
        url = f'/projects/{project.public_identifier}/'
        data = {'name': 'Project X', 'slug': 'PRJX', 'team': team.public_identifier}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 200
        p = models.Project.objects.get(pk=project.public_identifier)
        assert p.name == 'Project X'

    def test_update_deactivated_team(self, client, logged_in_user, deactivated_team, project):
        url = f'/projects/{project.public_identifier}/'
        data = {'name': 'Project X', 'slug': 'PRJX', 'team': deactivated_team.public_identifier}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 403

    def test_update_nonexistent_team(self, client, logged_in_user, project):
        url = f'/projects/{project.public_identifier}/'
        data = {'name': 'Project X', 'slug': 'PRJX', 'team': '00000000-0000-0000-0000-000000000000'}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 403

    def test_partial_update(self, client, logged_in_user, team, project):
        url = f'/projects/{project.public_identifier}/'
        data = {'name': 'Project X'}
        response = client.patch(url, data, content_type='application/json')
        assert response.status_code == 200
        p = models.Project.objects.get(pk=project.public_identifier)
        assert p.name == 'Project X'

    def test_create(self, client, logged_in_user, team, project):
        url = f'/projects/'
        data = {'name': 'Project X', 'slug': 'PRJX', 'team': team.public_identifier}
        response = client.post(url, data=data, content_type='application/json')
        assert response.status_code == 201
        p = models.Project.objects.get(name='Project X')
        assert p.name == 'Project X'
        assert models.Project.objects.count() == 2
