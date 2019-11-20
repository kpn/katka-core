from uuid import UUID

import pytest
from katka import models


@pytest.mark.django_db
class TestCredentialSecretList:
    def test_unauthenticated(self, client, team, credential, secret):
        url = f"/credentials/{credential.public_identifier}/secrets/"
        response = client.get(url)
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_authenticated(self, client, logged_in_user, team, credential, secret):
        response = client.get(f"/credentials/{credential.public_identifier}/secrets/")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1  # this also tests the not_my_credential and deactivated credential cases
        secret = parsed[0]
        assert secret["key"] == "access_token"
        assert secret["value"] == "full_access_value"
        assert UUID(secret["credential"]) == credential.public_identifier


@pytest.mark.django_db
class TestCredentialSecretGet:
    def test_unauthenticated(self, client, team, credential, secret):
        url = f"/credentials/{credential.public_identifier}/secrets/{secret.key}/"
        response = client.get(url)
        assert response.status_code == 404

    def test_authenticated(self, client, logged_in_user, team, credential, secret):
        url = f"/credentials/{credential.public_identifier}/secrets/{secret.key}/"
        response = client.get(url)
        assert response.status_code == 200
        secret = response.json()
        assert secret["key"] == "access_token"
        assert secret["value"] == "full_access_value"
        assert UUID(secret["credential"]) == credential.public_identifier

    def test_non_existent(self, client, logged_in_user, team, credential, secret):
        url = f"/credentials/00000000-0000-0000-0000-000000000000/secrets/{secret.key}/"
        response = client.get(url)
        assert response.status_code == 404

    def test_not_my_credential(self, client, logged_in_user, team, not_my_credential, secret):
        url = f"/credentials/{not_my_credential.public_identifier}/secrets/{secret.key}/"
        response = client.get(url)
        assert response.status_code == 404

    def test_excludes_inactive(self, client, logged_in_user, team, credential, deactivated_secret):
        url = f"/credentials/{credential.public_identifier}/secrets/{deactivated_secret.key}/"
        response = client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestCredentialSecretDelete:
    def test_unauthenticated(self, client, team, credential, secret):
        url = f"/credentials/{credential.public_identifier}/secrets/{secret.key}/"
        response = client.delete(url)
        assert response.status_code == 404

    def test_authenticated(self, client, logged_in_user, team, credential, secret):
        url = f"/credentials/{credential.public_identifier}/secrets/{secret.key}/"
        response = client.delete(url)
        assert response.status_code == 204
        s = models.CredentialSecret.objects.get(key=secret.key, credential=credential)
        assert s.deleted is True

    def test_non_existent(self, client, logged_in_user, team, credential, secret):
        before_count = models.CredentialSecret.objects.count()
        url = f"/credentials/00000000-0000-0000-0000-000000000000/secrets/{secret.key}/"
        response = client.delete(url)
        assert response.status_code == 404
        assert models.CredentialSecret.objects.count() == before_count

    def test_deactivated(self, client, logged_in_user, team, credential, deactivated_secret):
        url = f"/credentials/{credential.public_identifier}/secrets/{deactivated_secret.key}/"
        response = client.delete(url)
        assert response.status_code == 404
        s = models.CredentialSecret.objects.get(key=deactivated_secret.key, credential=credential)
        assert s.deleted is True

    def test_not_my_credential(self, client, logged_in_user, team, not_my_credential, not_my_secret):
        url = f"/credentials/{not_my_credential.public_identifier}/secrets/{not_my_secret.key}/"
        response = client.delete(url)
        assert response.status_code == 404
        s = models.CredentialSecret.objects.get(key=not_my_secret.key, credential=not_my_credential)
        assert s.deleted is False


@pytest.mark.django_db
class TestCredentialSecretUpdate:
    def test_unauthenticated(self, client, team, credential, secret):
        url = f"/credentials/{credential.public_identifier}/secrets/{secret.key}/"
        data = {"name": "B-Team", "group": "group1"}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 404

    def test_authenticated(self, client, logged_in_user, team, credential, secret):
        url = f"/credentials/{credential.public_identifier}/secrets/{secret.key}/"
        data = {"key": "access_token", "value": "new value"}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 200
        s = models.CredentialSecret.objects.get(key=secret.key, credential=credential)
        assert s.value == "new value"

    def test_non_existent(self, client, logged_in_user, team, credential, secret):
        url = f"/credentials/00000000-0000-0000-0000-000000000000/secrets/{secret.key}/"
        data = {"key": "access_token", "value": "new value"}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 404

    def test_deactivated(self, client, logged_in_user, team, credential, deactivated_secret):
        url = f"/credentials/{credential.public_identifier}/secrets/{deactivated_secret.key}/"
        data = {"key": "access_token", "value": "new value"}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 404
        s = models.CredentialSecret.objects.get(key=deactivated_secret.key, credential=credential)
        assert s.value == "full_access_value"

    def test_not_my_credential(self, client, logged_in_user, team, not_my_credential, not_my_secret):
        url = f"/credentials/{not_my_credential.public_identifier}/secrets/{not_my_secret.key}/"
        data = {"key": "access_token", "value": "new value"}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 404
        s = models.CredentialSecret.objects.get(key=not_my_secret.key, credential=not_my_credential)
        assert s.value == "full_access_value"


@pytest.mark.django_db
class TestCredentialSecretPartialUpdate:
    def test_unauthenticated(self, client, team, credential, secret):
        url = f"/credentials/{credential.public_identifier}/secrets/{secret.key}/"
        response = client.patch(url, {"name": "B-Team"}, content_type="application/json")
        assert response.status_code == 404

    def test_authenticated(self, client, logged_in_user, team, credential, secret):
        url = f"/credentials/{credential.public_identifier}/secrets/{secret.key}/"
        data = {"value": "new value"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 200
        s = models.CredentialSecret.objects.get(key=secret.key, credential=credential)
        assert s.value == "new value"

    def test_non_existent(self, client, logged_in_user, team, credential, secret):
        url = f"/credentials/00000000-0000-0000-0000-000000000000/secrets/{secret.key}/"
        data = {"value": "new value"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 404

    def test_deactivated(self, client, logged_in_user, team, credential, deactivated_secret):
        url = f"/credentials/{credential.public_identifier}/secrets/{deactivated_secret.key}/"
        data = {"value": "new value"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 404
        s = models.CredentialSecret.objects.get(key=deactivated_secret.key, credential=credential)
        assert s.value == "full_access_value"

    def test_not_my_credential(self, client, logged_in_user, team, not_my_credential, not_my_secret):
        url = f"/credentials/{not_my_credential.public_identifier}/secrets/{not_my_secret.key}/"
        data = {"value": "new value"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 404
        s = models.CredentialSecret.objects.get(key=not_my_secret.key, credential=not_my_credential)
        assert s.value == "full_access_value"


@pytest.mark.django_db
class TestCredentialSecretCreate:
    def test_unauthenticated(self, client, team, credential):
        url = f"/credentials/{credential.public_identifier}/secrets/"
        data = {"key": "access_token", "value": "my_secret_access_token"}
        response = client.post(url, data, content_type="application/json")
        assert response.status_code == 403

    def test_authenticated(self, client, logged_in_user, team, credential):
        before_count = models.CredentialSecret.objects.count()
        url = f"/credentials/{credential.public_identifier}/secrets/"
        response = client.post(url, {"key": "access_token", "value": "new value"}, content_type="application/json")
        assert response.status_code == 201
        assert models.CredentialSecret.objects.get(key="access_token", credential=credential)
        assert models.CredentialSecret.objects.count() == before_count + 1

    def test_non_existent(self, client, logged_in_user, team, credential):
        before_count = models.CredentialSecret.objects.count()
        url = f"/credentials/00000000-0000-0000-0000-000000000000/secrets/"
        response = client.post(url, {"key": "access_token", "value": "new value"}, content_type="application/json")
        assert response.status_code == 403
        assert models.CredentialSecret.objects.count() == before_count

    def test_deactivated(self, client, logged_in_user, team, deactivated_credential):
        before_count = models.CredentialSecret.objects.count()
        url = f"/credentials/{deactivated_credential.public_identifier}/secrets/"
        response = client.post(url, {"key": "access_token", "value": "new value"}, content_type="application/json")
        assert response.status_code == 403
        assert models.CredentialSecret.objects.count() == before_count

    def test_not_my_credential(self, client, logged_in_user, team, not_my_credential):
        before_count = models.CredentialSecret.objects.count()
        url = f"/credentials/{not_my_credential.public_identifier}/secrets/"
        response = client.post(url, {"key": "access_token", "value": "new value"}, content_type="application/json")
        assert response.status_code == 403
        assert models.CredentialSecret.objects.count() == before_count
