from django.contrib.auth.models import Group, User

import pytest
from katka import models
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
    team.deleted = True
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
    project.deleted = True
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
    secret.deleted = True
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


@pytest.fixture
def scm_service():
    scm_service = models.SCMService(type='bitbucket', server_url='www.example.com')
    with username_on_model(models.SCMService, 'initial'):
        scm_service.save()

    return scm_service


@pytest.fixture
def deactivated_scm_service(scm_service):
    scm_service.deleted = True
    with username_on_model(models.SCMService, 'initial'):
        scm_service.save()

    return scm_service


@pytest.fixture
def scm_repository(scm_service, credential):
    scm_repository = models.SCMRepository(scm_service=scm_service, credential=credential,
                                          organisation='acme', repository_name='sample')
    with username_on_model(models.SCMRepository, 'initial'):
        scm_repository.save()

    return scm_repository


@pytest.fixture
def deactivated_scm_repository(scm_repository):
    scm_repository.deleted = True
    with username_on_model(models.SCMRepository, 'initial'):
        scm_repository.save()

    return scm_repository


@pytest.fixture
def application(project, scm_repository):
    application = models.Application(project=project, scm_repository=scm_repository, name='Application D', slug='APPD')
    with username_on_model(models.Application, 'initial'):
        application.save()

    return application


@pytest.fixture
def deactivated_application(application):
    application.deleted = True
    with username_on_model(models.Application, 'initial'):
        application.save()

    return application
