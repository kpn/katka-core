from uuid import UUID

from django.contrib.auth.models import Group, User

import pytest
from katka import models
from katka.constants import STATUS_INACTIVE
from katka.fields import username_on_model


@pytest.fixture
def group():
    group = Group(name='group1')
    group.save()
    return group


@pytest.fixture
def team(group):
    a_team = models.Team(name='A-Team', group=group)
    with username_on_model(models.Team, 'initial'):
        a_team.save()

    return a_team


@pytest.fixture
def deactivated_team(team):
    team.status = STATUS_INACTIVE
    with username_on_model(models.Team, 'deactivator'):
        team.save()

    return team


@pytest.fixture
def user(group):
    u = User.objects.create_user('test_user', None, None)
    u.groups.add(group)
    return u


@pytest.mark.django_db
class TestTeamViewSetUnauthenticated:
    """
    When a user is not logged in, no group information is available, so nothing is returned.

    For listing, that would be an empty list for other operations, an error like the object could
    not be found, except on create (you need to be part of a group and anonymous users do not have any)
    """

    def test_list(self, client, team):
        response = client.get('/team/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, team):
        response = client.get(f'/team/{team.public_identifier}/')
        assert response.status_code == 404

    def test_delete(self, client, team):
        response = client.delete(f'/team/{team.public_identifier}/')
        assert response.status_code == 404

    def test_update(self, client, team):
        data = {'name': 'B-Team', 'group': 'group1'}
        response = client.put(f'/team/{team.public_identifier}/', data, content_type='application/json')
        assert response.status_code == 404

    def test_partial_update(self, client, team):
        response = client.patch(f'/team/{team.public_identifier}/', {'name': 'B-Team'},
                                content_type='application/json')
        assert response.status_code == 404

    def test_create(self, client, team, group):
        response = client.post(f'/team/', {'name': 'B-Team', 'group': group.name}, content_type='application/json')
        assert response.status_code == 403


@pytest.mark.django_db
class TestTeamViewSet:
    def test_list(self, client, team, user):
        client.force_login(user)
        response = client.get('/team/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]['name'] == 'A-Team'
        assert parsed[0]['group'] == 'group1'
        UUID(parsed[0]['public_identifier'])  # should not raise

    def test_list_excludes_inactive(self, client, deactivated_team, user):
        client.force_login(user)
        response = client.get('/team/')
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, team, user):
        client.force_login(user)
        response = client.get(f'/team/{team.public_identifier}/')
        assert response.status_code == 200
        parsed = response.json()
        assert parsed['name'] == 'A-Team'
        assert parsed['group'] == 'group1'
        UUID(parsed['public_identifier'])  # should not raise

    def test_get_excludes_inactive(self, client, deactivated_team, user):
        client.force_login(user)
        response = client.get(f'/team/{deactivated_team.public_identifier}/')
        assert response.status_code == 404

    def test_delete(self, client, team, user):
        client.force_login(user)
        response = client.delete(f'/team/{team.public_identifier}/')
        assert response.status_code == 204
        t = models.Team.objects.get(pk=team.public_identifier)
        assert t.status == STATUS_INACTIVE

    def test_update(self, client, team, user):
        client.force_login(user)
        data = {'name': 'B-Team', 'group': 'group1'}
        response = client.put(f'/team/{team.public_identifier}/', data, content_type='application/json')
        assert response.status_code == 200
        t = models.Team.objects.get(pk=team.public_identifier)
        assert t.name == 'B-Team'

    def test_partial_update(self, client, team, user):
        client.force_login(user)
        response = client.patch(f'/team/{team.public_identifier}/', {'name': 'B-Team'},
                                content_type='application/json')
        assert response.status_code == 200
        t = models.Team.objects.get(pk=team.public_identifier)
        assert t.name == 'B-Team'

    def test_change_group_non_member(self, client, team, user):
        group2 = Group(name='group2')
        group2.save()
        client.force_login(user)
        response = client.patch(f'/team/{team.public_identifier}/', {'group': 'group2'},
                                content_type='application/json')
        assert response.status_code == 403

    def test_change_group_not_exists(self, client, team, user):
        client.force_login(user)
        response = client.patch(f'/team/{team.public_identifier}/', {'group': 'group2'},
                                content_type='application/json')
        assert response.status_code == 404

    def test_create(self, client, team, group, user):
        client.force_login(user)
        response = client.post(f'/team/', {'name': 'B-Team', 'group': group.name}, content_type='application/json')
        assert response.status_code == 201
        t = models.Team.objects.get(name='B-Team')
        assert t.name == 'B-Team'
        assert models.Team.objects.count() == 2
