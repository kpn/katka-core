from uuid import UUID

import pytest
from katka import models


@pytest.mark.django_db
class TestCredentialViewSet:
    def test_list(self, client, logged_in_user, team, credential):
        response = client.get(f"/credentials/")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 3
        credential_teamx = [c for c in parsed if c["name"] == "System user X"]
        assert len(credential_teamx) == 1
        credential_teamx = credential_teamx[0]
        assert UUID(credential_teamx["public_identifier"]) == credential.public_identifier
        parsed_team = credential_teamx["team"]
        assert UUID(parsed_team) == team.public_identifier

    def test_filtered_list(self, client, logged_in_user, team, credential, my_other_team, my_other_teams_credential):

        response = client.get("/credentials/?team=" + str(my_other_team.public_identifier))
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert UUID(parsed[0]["public_identifier"]) == my_other_teams_credential.public_identifier
        assert parsed[0]["name"] == "System user my other team"
        parsed_team = parsed[0]["team"]
        assert UUID(parsed_team) == my_other_team.public_identifier

    def test_filtered_list_non_existing_team(
        self, client, logged_in_user, team, credential, my_other_team, my_other_teams_credential
    ):

        response = client.get("/credentials/?team=12345678-1234-5678-1234-567812345678")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, logged_in_user, team, credential):
        response = client.get(f"/credentials/{credential.public_identifier}/")
        assert response.status_code == 200
        parsed = response.json()
        assert UUID(parsed["public_identifier"]) == credential.public_identifier
        assert parsed["name"] == "System user X"
        assert UUID(parsed["team"]) == team.public_identifier

    def test_get_excludes_inactive(self, client, logged_in_user, deactivated_team):
        response = client.get(f"/team/{deactivated_team.public_identifier}/")
        assert response.status_code == 404

    def test_delete(self, client, logged_in_user, team, credential):
        response = client.delete(f"/credentials/{credential.public_identifier}/")
        assert response.status_code == 204
        p = models.Credential.objects.get(pk=credential.public_identifier)
        assert p.deleted is True

    def test_update(self, client, logged_in_user, team, credential):
        url = f"/credentials/{credential.public_identifier}/"
        data = {"name": "System user Y", "team": team.public_identifier}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 200
        p = models.Credential.objects.get(pk=credential.public_identifier)
        assert p.name == "System user Y"

    def test_update_nonexistent_team(self, client, logged_in_user, team, credential):
        url = f"/credentials/{credential.public_identifier}/"
        data = {"name": "System User Y", "team": "00000000-0000-0000-0000-000000000000"}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 403

    def test_partial_update(self, client, logged_in_user, team, credential):
        url = f"/credentials/{credential.public_identifier}/"
        data = {"name": "System User Y"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 200
        p = models.Credential.objects.get(pk=credential.public_identifier)
        assert p.name == "System User Y"

    def test_create(self, client, logged_in_user, team, credential):
        before_count = models.Credential.objects.count()
        url = f"/credentials/"
        data = {"name": "System User Y", "team": team.public_identifier}
        response = client.post(url, data=data, content_type="application/json")
        assert response.status_code == 201
        models.Credential.objects.get(name="System User Y")
        assert models.Credential.objects.count() == before_count + 1
