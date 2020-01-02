from uuid import UUID

import pytest
from katka import models


@pytest.mark.django_db
class TestProjectViewSet:
    def test_list(self, client, logged_in_user, my_team, my_project):
        response = client.get("/projects/")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]["name"] == "Project D"
        assert parsed[0]["slug"] == "PRJD"
        parsed_team = parsed[0]["team"]
        assert UUID(parsed_team) == my_team.public_identifier

    def test_filtered_list(self, client, logged_in_user, my_team, my_project, my_other_team, my_other_project):
        response = client.get("/projects/?team=" + str(my_other_team.public_identifier))
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]["name"] == "Project 2"
        assert parsed[0]["slug"] == "PRJ2"
        parsed_team = parsed[0]["team"]
        assert UUID(parsed_team) == my_other_team.public_identifier

    def test_filtered_list_non_existing_team(
        self, client, logged_in_user, my_team, my_project, my_other_team, my_other_project
    ):
        response = client.get("/applications/?project=12345678-1234-5678-1234-567812345678")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_list_excludes_inactive(self, client, logged_in_user, my_team, deactivated_project):
        response = client.get("/projects/")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, logged_in_user, my_team, my_project):
        response = client.get(f"/projects/{my_project.public_identifier}/")
        assert response.status_code == 200
        parsed = response.json()
        assert parsed["name"] == "Project D"
        assert parsed["slug"] == "PRJD"
        assert UUID(parsed["team"]) == my_team.public_identifier

    def test_get_excludes_inactive(self, client, logged_in_user, my_team, deactivated_project):
        response = client.get(f"/projects/{deactivated_project.public_identifier}/")
        assert response.status_code == 404

    def test_delete(self, client, logged_in_user, my_team, my_project):
        response = client.delete(f"/projects/{my_project.public_identifier}/")
        assert response.status_code == 204
        p = models.Project.objects.get(pk=my_project.public_identifier)
        assert p.deleted is True

    def test_update(self, client, logged_in_user, my_team, my_project):
        url = f"/projects/{my_project.public_identifier}/"
        data = {"name": "Project X", "slug": "PRJX", "team": my_team.public_identifier}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 200
        p = models.Project.objects.get(pk=my_project.public_identifier)
        assert p.name == "Project X"

    def test_update_deactivated_team(self, client, logged_in_user, deactivated_team, my_project):
        url = f"/projects/{my_project.public_identifier}/"
        data = {"name": "Project X", "slug": "PRJX", "team": deactivated_team.public_identifier}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 403

    def test_update_nonexistent_team(self, client, logged_in_user, my_project):
        url = f"/projects/{my_project.public_identifier}/"
        data = {"name": "Project X", "slug": "PRJX", "team": "00000000-0000-0000-0000-000000000000"}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 403

    def test_partial_update(self, client, logged_in_user, my_team, my_project):
        url = f"/projects/{my_project.public_identifier}/"
        data = {"name": "Project X"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 200
        p = models.Project.objects.get(pk=my_project.public_identifier)
        assert p.name == "Project X"

    def test_create(self, client, logged_in_user, my_team, my_project):
        before = models.Project.objects.count()
        url = f"/projects/"
        data = {"name": "Project X", "slug": "PRJX", "team": my_team.public_identifier}
        response = client.post(url, data=data, content_type="application/json")
        assert response.status_code == 201
        p = models.Project.objects.get(name="Project X")
        assert p.name == "Project X"
        assert models.Project.objects.count() == before + 1
