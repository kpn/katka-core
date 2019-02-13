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
def not_my_group():
    group = Group(name='not_my_group')
    group.save()
    return group


@pytest.fixture
def not_my_team(not_my_group):
    z_team = models.Team(name='Z-Team', slug='ZTM', group=not_my_group)

    with username_on_model(models.Team, 'initial'):
        z_team.save()

    return z_team


@pytest.fixture
def my_team(group):
    a_team = models.Team(name='A-Team', slug='ATM', group=group)

    with username_on_model(models.Team, 'initial'):
        a_team.save()

    return a_team


@pytest.fixture
def team(my_team, not_my_team):
    """Return my team, but also make sure that 'not_my_team' is active so we can test if it is excluded, etc."""
    return my_team


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
def secret(credential):
    secret = models.CredentialSecret(key='access_token', value='full_access_value', credential=credential)
    with username_on_model(models.CredentialSecret, 'initial'):
        secret.save()

    return secret


@pytest.fixture
def deactivated_secret(secret):
    secret.status = 'inactive'
    with username_on_model(models.CredentialSecret, 'initial'):
        secret.save()

    return secret


@pytest.fixture
def user(group):
    u = User.objects.create_user('test_user', None, None)
    u.groups.add(group)
    return u


@pytest.fixture
def logged_in_user(client, user):
    client.force_login(user)
    return user
