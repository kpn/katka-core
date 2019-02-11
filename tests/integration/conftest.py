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
    a_team = models.Team(name='A-Team', slug='ATM', group=group)
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
def project(team):
    project = models.Project(team=team, name='Project D', slug='PRJD')
    with username_on_model(models.Project, 'initial'):
        project.save()

    return project


@pytest.fixture
def deactivated_project(team, project):
    project.status = 'inactive'
    with username_on_model(models.Project, 'initial'):
        project.save()

    return project


@pytest.fixture
def credential(team):
    credential = models.Credential(name='System user X', slug='SUX', team=team)
    with username_on_model(models.Credential, 'initial'):
        credential.save()

    return credential


@pytest.fixture
def user(group):
    u = User.objects.create_user('test_user', None, None)
    u.groups.add(group)
    return u


@pytest.fixture
def logged_in_user(client, user):
    client.force_login(user)
    return user
