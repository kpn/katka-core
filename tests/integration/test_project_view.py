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

    def test_list(self, client, team, project):
        response = client.get(f'/team/{team.public_identifier}/project/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_list_unknown_team(self, client, team, project):
        response = client.get('/team/00000000-0000-0000-0000-000000000000/project/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, team, project):
        response = client.get(f'/team/{team.public_identifier}/project/{project.name}/')
        assert response.status_code == 404

    def test_delete(self, client, team, project):
        response = client.delete(f'/team/{team.public_identifier}/project/{project.name}/')
        assert response.status_code == 404

    def test_update(self, client, team, project):
        url = f'/team/{team.public_identifier}/project/{project.name}/'
        data = {'name': 'B-Team', 'group': 'group1'}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 404

    def test_partial_update(self, client, team, project):
        url = f'/team/{team.public_identifier}/project/{project.name}/'
        response = client.patch(url, {'name': 'B-Team'}, content_type='application/json')
        assert response.status_code == 404

    def test_create(self, client, team):
        url = f'/team/{team.public_identifier}/project/'
        data = {'name': 'Project D'}
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 403


@pytest.mark.django_db
class TestProjectViewSet:
    def test_list(self, client, logged_in_user, team, project):
        response = client.get(f'/team/{team.public_identifier}/project/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]['name'] == 'Project D'
        assert parsed[0]['slug'] == 'PRJD'
        parsed_team = parsed[0]['team']
        assert UUID(parsed_team['public_identifier']) == team.public_identifier
        assert parsed_team['slug'] == 'ATM'

    def test_list_excludes_inactive(self, client, logged_in_user, team, deactivated_project):
        response = client.get(f'/team/{team.public_identifier}/project/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, logged_in_user, team, project):
        response = client.get(f'/team/{team.public_identifier}/project/{project.public_identifier}/')
        assert response.status_code == 200
        parsed = response.json()
        assert parsed['name'] == 'Project D'
        assert parsed['team']['slug'] == 'ATM'
        assert UUID(parsed['team']['public_identifier']) == team.public_identifier

    def test_get_excludes_inactive(self, client, logged_in_user, deactivated_team):
        response = client.get(f'/team/{deactivated_team.public_identifier}/')
        assert response.status_code == 404

    def test_delete(self, client, logged_in_user, team, project):
        response = client.delete(f'/team/{team.public_identifier}/project/{project.public_identifier}/')
        assert response.status_code == 204
        p = models.Project.objects.get(pk=project.public_identifier)
        assert p.status == STATUS_INACTIVE

    def test_update(self, client, logged_in_user, team, project):
        url = f'/team/{team.public_identifier}/project/{project.public_identifier}/'
        data = {'name': 'Project X'}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 200
        p = models.Project.objects.get(pk=project.public_identifier)
        assert p.name == 'Project X'

    def test_update_nonexistent_team(self, client, logged_in_user, team, project):
        url = f'/team/00000000-0000-0000-0000-000000000000/project/{project.public_identifier}/'
        data = {'name': 'Project X'}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 404

    def test_partial_update(self, client, logged_in_user, team, project):
        url = f'/team/{team.public_identifier}/project/{project.public_identifier}/'
        data = {'name': 'Project X'}
        response = client.patch(url, data, content_type='application/json')
        assert response.status_code == 200
        p = models.Project.objects.get(pk=project.public_identifier)
        assert p.name == 'Project X'

    def test_create(self, client, logged_in_user, team, project):
        url = f'/team/{team.public_identifier}/project/'
        response = client.post(url, {'name': 'Project X'}, content_type='application/json')
        assert response.status_code == 201
        p = models.Project.objects.get(name='Project X')
        assert p.name == 'Project X'
        assert models.Project.objects.count() == 2
