from uuid import UUID

import pytest
from katka import models
from katka.constants import STATUS_INACTIVE


@pytest.mark.django_db
class TestCredentialViewSetUnauthenticated:
    """
    When a user is not logged in, no group information is available, so nothing is returned.

    For listing, that would be an empty list for other operations, an error like the object could
    not be found, except on create (you need to be part of a group and anonymous users do not have any)
    """

    def test_list(self, client, team, credential):
        response = client.get(f'/credentials/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_list_unknown_team(self, client, team, credential):
        response = client.get('/credentials/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, team, credential):
        response = client.get(f'/credentials/{credential.public_identifier}/')
        assert response.status_code == 404

    def test_delete(self, client, team, credential):
        response = client.delete(f'/credentials/{credential.public_identifier}/')
        assert response.status_code == 404

    def test_update(self, client, team, credential):
        url = f'/credentials/{credential.public_identifier}/'
        data = {'name': 'B-Team', 'group': 'group1'}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 404

    def test_partial_update(self, client, team, credential):
        url = f'/credentials/{credential.public_identifier}/'
        response = client.patch(url, {'name': 'B-Team'}, content_type='application/json')
        assert response.status_code == 404

    def test_create(self, client, team):
        url = f'/credentials/'
        data = {'name': 'System User Y', 'slug': 'SUY', 'team': team.public_identifier}
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 403


@pytest.mark.django_db
class TestCredentialViewSet:
    def test_list(self, client, logged_in_user, team, credential):
        response = client.get(f'/credentials/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]['name'] == 'System user X'
        parsed_team = parsed[0]['team']
        assert UUID(parsed_team) == team.public_identifier

    def test_get(self, client, logged_in_user, team, credential):
        response = client.get(f'/credentials/{credential.public_identifier}/')
        assert response.status_code == 200
        parsed = response.json()
        assert parsed['name'] == 'System user X'
        assert UUID(parsed['team']) == team.public_identifier

    def test_get_excludes_inactive(self, client, logged_in_user, deactivated_team):
        response = client.get(f'/team/{deactivated_team.public_identifier}/')
        assert response.status_code == 404

    def test_delete(self, client, logged_in_user, team, credential):
        response = client.delete(f'/credentials/{credential.public_identifier}/')
        assert response.status_code == 204
        p = models.Credential.objects.get(pk=credential.public_identifier)
        assert p.status == STATUS_INACTIVE

    def test_update(self, client, logged_in_user, team, credential):
        url = f'/credentials/{credential.public_identifier}/'
        data = {'name': 'System user Y', 'slug': 'SUY', 'team': team.public_identifier}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 200
        p = models.Credential.objects.get(pk=credential.public_identifier)
        assert p.name == 'System user Y'

    def test_update_nonexistent_team(self, client, logged_in_user, team, credential):
        url = f'/credentials/{credential.public_identifier}/'
        data = {'name': 'System User Y', 'slug': 'SUY', 'team': '00000000-0000-0000-0000-000000000000'}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 403

    def test_partial_update(self, client, logged_in_user, team, credential):
        url = f'/credentials/{credential.public_identifier}/'
        data = {'name': 'System User Y'}
        response = client.patch(url, data, content_type='application/json')
        assert response.status_code == 200
        p = models.Credential.objects.get(pk=credential.public_identifier)
        assert p.name == 'System User Y'

    def test_create(self, client, logged_in_user, team, credential):
        url = f'/credentials/'
        data = {'name': 'System User Y', 'slug': 'SUY', 'team': team.public_identifier}
        response = client.post(url, data=data, content_type='application/json')
        assert response.status_code == 201
        models.Credential.objects.get(name='System User Y')
        assert models.Credential.objects.count() == 2
