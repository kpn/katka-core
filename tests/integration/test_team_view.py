from uuid import UUID

import pytest
from katka import models
from tests.integration.conftest import scoped_client


@pytest.mark.django_db
class TestTeamViewSet:
    def test_list(self, client, logged_in_user, my_team):
        response = client.get("/teams/")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]["name"] == "A-Team"
        assert parsed[0]["group"] == "group1"
        UUID(parsed[0]["public_identifier"])  # should not raise

    def test_filtered_list(self, client, logged_in_user, my_team, group, my_other_team, my_other_group):
        """Note: Can only filter teams that logged_in_user belongs to"""
        # TODO: Filter on group name rather than id
        response = client.get("/teams/?group=" + str(my_other_group.id))
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]["name"] == "B-Team"
        assert parsed[0]["group"] == "my_other_group"
        UUID(parsed[0]["public_identifier"])  # should not raise

    def test_filtered_list_non_existing_group(self, client, logged_in_user, team, my_other_team):

        response = client.get("/teams/?group=1289572137892789")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_list_excludes_inactive(self, client, logged_in_user, deactivated_team):
        response = client.get("/teams/")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, logged_in_user, team):
        response = client.get(f"/teams/{team.public_identifier}/")
        assert response.status_code == 200
        parsed = response.json()
        assert parsed["name"] == "A-Team"
        assert parsed["group"] == "group1"
        UUID(parsed["public_identifier"])  # should not raise

    def test_get_by_project(self, client, logged_in_user, team, project):
        response = client.get(f"/teams/{team.public_identifier}/?project={project.public_identifier}")
        assert response.status_code == 200
        parsed = response.json()
        assert parsed["name"] == "A-Team"
        assert parsed["group"] == "group1"
        UUID(parsed["public_identifier"])  # should not raise

    def test_get_by_project_bad(self, client, logged_in_user, team, project):
        response = client.get(f"/teams/{team.public_identifier}/?project=12345")
        assert response.status_code == 404

    def test_get_by_application(self, client, logged_in_user, team, application):
        response = client.get(f"/teams/{team.public_identifier}/?application={application.public_identifier}")
        assert response.status_code == 200
        parsed = response.json()
        assert parsed["name"] == "A-Team"
        assert parsed["group"] == "group1"
        UUID(parsed["public_identifier"])  # should not raise

    def test_get_by_application_bad(self, client, logged_in_user, team, application):
        response = client.get(f"/teams/{team.public_identifier}/?application=12345")
        assert response.status_code == 404

    def test_get_excludes_inactive(self, client, logged_in_user, deactivated_team):
        response = client.get(f"/teams/{deactivated_team.public_identifier}/")
        assert response.status_code == 404

    def test_delete(self, client, logged_in_user, my_team):
        response = client.delete(f"/teams/{my_team.public_identifier}/")
        assert response.status_code == 204
        t = models.Team.objects.get(pk=my_team.public_identifier)
        assert t.deleted is True

    def test_update(self, client, logged_in_user, my_team):
        data = {"name": "B-Team", "slug": "BTM", "group": "group1"}
        response = client.put(f"/teams/{my_team.public_identifier}/", data, content_type="application/json")
        assert response.status_code == 200
        t = models.Team.objects.get(pk=my_team.public_identifier)
        assert t.name == "B-Team"

    def test_partial_update(self, client, logged_in_user, my_team):
        data = {"name": "B-Team"}
        response = client.patch(f"/teams/{my_team.public_identifier}/", data, content_type="application/json")
        assert response.status_code == 200
        t = models.Team.objects.get(pk=my_team.public_identifier)
        assert t.name == "B-Team"

    def test_change_group_non_member(self, client, user, my_team, not_my_group):
        client.force_login(user)
        response = client.patch(
            f"/teams/{my_team.public_identifier}/", {"group": not_my_group.name}, content_type="application/json"
        )
        assert response.status_code == 403

    def test_change_group_scoped_user(self, not_my_group, my_team):
        """Even though the fixture has 'not_my' and 'my_', the scoped user can touch everything"""
        with scoped_client() as client:
            response = client.patch(
                f"/teams/{my_team.public_identifier}/", {"group": not_my_group.name}, content_type="application/json"
            )

        assert response.status_code == 200

    def test_change_group_not_exists(self, client, logged_in_user, my_team):
        response = client.patch(
            f"/teams/{my_team.public_identifier}/", {"group": "group2"}, content_type="application/json"
        )
        assert response.status_code == 404

    def test_create(self, client, logged_in_user, my_team, group):
        before_count = models.Team.objects.count()
        data = {"name": "B-Team", "slug": "BTM", "group": group.name}
        response = client.post(f"/teams/", data, content_type="application/json")
        assert response.status_code == 201
        t = models.Team.objects.get(name="B-Team")
        assert t.name == "B-Team"
        assert models.Team.objects.count() == before_count + 1
