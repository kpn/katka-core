from uuid import UUID

import pytest
from katka import models
from katka.constants import STATUS_INACTIVE


@pytest.mark.django_db
class TestCredentialSecretViewSetUnauthenticated:
    """
    When a user is not logged in, no group information is available, so nothing is returned.

    For listing, that would be an empty list for other operations, an error like the object could
    not be found, except on create (you need to be part of a group and anonymous users do not have any)
    """

    def test_list(self, client, team, credential, secret):
        url = f'/team/{team.public_identifier}/credential/{credential.public_identifier}/secrets/'
        response = client.get(url)
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_list_unknown_team(self, client, team, credential, secret):
        unknown_pui = '00000000-0000-0000-0000-000000000000'
        url = f'/team/{unknown_pui}/credential/{credential.public_identifier}/secrets/'
        response = client.get(url)
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, team, credential, secret):
        url = f'/team/{team.public_identifier}/credential/{credential.public_identifier}/secrets/{secret.key}/'
        response = client.get(url)
        assert response.status_code == 404

    def test_delete(self, client, team, credential, secret):
        url = f'/team/{team.public_identifier}/credential/{credential.public_identifier}/secrets/{secret.key}/'
        response = client.delete(url)
        assert response.status_code == 404

    def test_update(self, client, team, credential, secret):
        url = f'/team/{team.public_identifier}/credential/{credential.public_identifier}/secrets/{secret.key}/'
        data = {'name': 'B-Team', 'group': 'group1'}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 404

    def test_partial_update(self, client, team, credential, secret):
        url = f'/team/{team.public_identifier}/credential/{credential.public_identifier}/secrets/{secret.key}/'
        response = client.patch(url, {'name': 'B-Team'}, content_type='application/json')
        assert response.status_code == 404

    def test_create(self, client, team, credential):
        url = f'/team/{team.public_identifier}/credential/{credential.public_identifier}/secrets/'
        data = {'key': 'access_token', 'value': 'my_secret_access_token'}
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 403


@pytest.mark.django_db
class TestCredentialViewSet:
    def test_list(self, client, logged_in_user, team, credential, secret):
        response = client.get(f'/team/{team.public_identifier}/credential/{credential.public_identifier}/secrets/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        secret = parsed[0]
        assert secret['key'] == 'access_token'
        assert secret['value'] == 'full_access_value'
        assert UUID(secret['credential']) == credential.public_identifier

    def test_get(self, client, logged_in_user, team, credential, secret):
        url = f'/team/{team.public_identifier}/credential/{credential.public_identifier}/secrets/{secret.key}/'
        response = client.get(url)
        assert response.status_code == 200
        secret = response.json()
        assert secret['key'] == 'access_token'
        assert secret['value'] == 'full_access_value'
        assert UUID(secret['credential']) == credential.public_identifier

    def test_get_excludes_inactive(self, client, logged_in_user, team, credential, deactivated_secret):
        url = f'/team/{team.public_identifier}/credential/{credential.public_identifier}/' + \
              f'secrets/{deactivated_secret.key}/'
        response = client.get(url)
        assert response.status_code == 404

    def test_delete(self, client, logged_in_user, team, credential, secret):
        url = f'/team/{team.public_identifier}/credential/{credential.public_identifier}/secrets/{secret.key}/'
        response = client.delete(url)
        assert response.status_code == 204
        s = models.CredentialSecret.objects.get(key=secret.key, credential=credential)
        assert s.status == STATUS_INACTIVE

    def test_update(self, client, logged_in_user, team, credential, secret):
        url = f'/team/{team.public_identifier}/credential/{credential.public_identifier}/secrets/{secret.key}/'
        data = {'key': 'access_token', 'value': 'new value'}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 200
        s = models.CredentialSecret.objects.get(key=secret.key, credential=credential)
        assert s.value == 'new value'

    def test_update_nonexistent_team(self, client, logged_in_user, team, credential, secret):
        unknown_pui = '00000000-0000-0000-0000-000000000000'
        url = f'/team/{unknown_pui}/credential/{credential.public_identifier}/secrets/{secret.key}/'
        data = {'key': 'access_token', 'value': 'new value'}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 404

    def test_partial_update(self, client, logged_in_user, team, credential, secret):
        url = f'/team/{team.public_identifier}/credential/{credential.public_identifier}/secrets/{secret.key}/'
        data = {'value': 'new value'}
        response = client.patch(url, data, content_type='application/json')
        assert response.status_code == 200
        s = models.CredentialSecret.objects.get(key=secret.key, credential=credential)
        assert s.value == 'new value'

    def test_create(self, client, logged_in_user, team, credential, secret):
        url = f'/team/{team.public_identifier}/credential/{credential.public_identifier}/secrets/'
        response = client.post(url, {'key': 'password', 'value': 'new value'}, content_type='application/json')
        assert response.status_code == 201
        models.CredentialSecret.objects.get(key='access_token', credential=credential)
        assert models.CredentialSecret.objects.count() == 2
