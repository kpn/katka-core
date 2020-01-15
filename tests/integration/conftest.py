import contextlib

from django.contrib.auth.models import Group, User
from django.test import Client, modify_settings, override_settings

import pytest
from katka import models
from katka.fields import username_on_model


@contextlib.contextmanager
def anonymous_client():
    yield Client()


@contextlib.contextmanager
def user_client():
    client = Client()
    user = User.objects.get(username="test_user")
    client.force_login(user)
    yield client


class AddScopesMiddleware:
    def __init__(self, handler):
        self.handler = handler

    def __call__(self, request):
        request.scopes = request.headers["Scopes"]
        return self.handler(request)


class ScopedClient(Client):
    def __init__(self, scopes, *args, **kwargs):
        self.scopes = scopes
        super().__init__(*args, **kwargs)

    def request(self, **request):
        request["HTTP_SCOPES"] = self.scopes
        return super().request(**request)


@contextlib.contextmanager
def scoped_client():
    scope_full_access = "super-access"
    scoped_client = ScopedClient((scope_full_access,))
    with modify_settings(MIDDLEWARE={"append": "tests.integration.conftest.AddScopesMiddleware"}), override_settings(
        SCOPE_FULL_ACCESS=scope_full_access
    ):
        yield scoped_client


@pytest.fixture
def my_group():
    group = Group(name="group1")
    group.save()
    return group


@pytest.fixture
def my_other_group():
    group = Group(name="my_other_group")
    group.save()
    return group


@pytest.fixture
def not_my_group():
    group = Group(name="not_my_group")
    group.save()
    return group


@pytest.fixture
def group(my_group, my_other_group, not_my_group):
    return my_group


@pytest.fixture
def not_my_team(not_my_group):
    team = models.Team(name="Z-Team", slug="ZTM", group=not_my_group)

    with username_on_model(models.Team, "initial"):
        team.save()

    return team


@pytest.fixture
def my_team(group, not_my_team):
    team = models.Team(name="A-Team", slug="ATM", group=group)

    with username_on_model(models.Team, "initial"):
        team.save()

    return team


@pytest.fixture
def my_other_team(my_other_group):
    team = models.Team(name="B-Team", slug="BTM", group=my_other_group)

    with username_on_model(models.Team, "initial"):
        team.save()

    return team


@pytest.fixture
def deactivated_team(my_group):
    team = models.Team(name="Deactivated-Team", slug="DTM", group=my_group)
    team.deleted = True
    with username_on_model(models.Team, "deactivator"):
        team.save()

    return team


@pytest.fixture
def team(my_team, my_other_team, not_my_team, deactivated_team):
    return my_team


@pytest.fixture
def not_my_project(not_my_team):
    project = models.Project(team=not_my_team, name="Project Not Mine", slug="NMP1")
    with username_on_model(models.Project, "initial"):
        project.save()

    return project


@pytest.fixture
def my_project(team, not_my_project):
    project = models.Project(team=team, name="Project D", slug="PRJD")
    with username_on_model(models.Project, "initial"):
        project.save()

    return project


@pytest.fixture
def my_other_project(my_other_team):
    project = models.Project(team=my_other_team, name="Project 2", slug="PRJ2")
    with username_on_model(models.Project, "initial"):
        project.save()

    return project


@pytest.fixture
def deactivated_project(my_team):
    project = models.Project(team=my_team, name="Project Deactivated", slug="PRJD2")
    project.deleted = True
    with username_on_model(models.Project, "initial"):
        project.save()

    return project


@pytest.fixture
def project(my_project, my_other_project, not_my_project, deactivated_project):
    return my_project


@pytest.fixture
def not_my_credential(not_my_team):
    credential = models.Credential(name="System user D", team=not_my_team)
    with username_on_model(models.Credential, "initial"):
        credential.save()

    return credential


@pytest.fixture
def my_credential(team, not_my_credential):
    credential = models.Credential(name="System user X", team=team)
    with username_on_model(models.Credential, "initial"):
        credential.save()

    return credential


@pytest.fixture
def my_other_credential(team):
    credential = models.Credential(name="System user other", team=team)
    with username_on_model(models.Credential, "initial"):
        credential.save()

    return credential


@pytest.fixture
def my_other_teams_credential(my_other_team):
    credential = models.Credential(name="System user my other team", team=my_other_team)
    with username_on_model(models.Credential, "initial"):
        credential.save()

    return credential


@pytest.fixture
def deactivated_credential(team):
    credential = models.Credential(name="System user deactivated", team=team)
    credential.deleted = True
    with username_on_model(models.Credential, "initial"):
        credential.save()

    return credential


@pytest.fixture
def credential(
    my_credential, my_other_credential, my_other_teams_credential, not_my_credential, deactivated_credential
):
    return my_credential


@pytest.fixture
def not_my_secret(not_my_credential):
    secret = models.CredentialSecret(key="access_token", value="full_access_value", credential=not_my_credential)
    with username_on_model(models.CredentialSecret, "initial"):
        secret.save()

    return secret


@pytest.fixture
def my_secret(my_credential, not_my_secret):
    secret = models.CredentialSecret(key="access_token", value="full_access_value", credential=my_credential)
    with username_on_model(models.CredentialSecret, "initial"):
        secret.save()

    return secret


@pytest.fixture
def my_other_secret(my_other_credential):
    secret = models.CredentialSecret(key="access_token", value="full_access_value", credential=my_other_credential)
    with username_on_model(models.CredentialSecret, "initial"):
        secret.save()

    return secret


@pytest.fixture
def deactivated_secret(credential):
    secret = models.CredentialSecret(key="username", value="full_access_value", credential=credential)
    secret.deleted = True
    with username_on_model(models.CredentialSecret, "initial"):
        secret.save()

    return secret


@pytest.fixture
def secret(my_secret, my_other_secret, not_my_secret, deactivated_secret):
    return my_secret


@pytest.fixture
def user(group, my_other_group):
    u = User.objects.create_user("test_user", None, None)
    u.groups.add(group)
    u.groups.add(my_other_group)
    return u


@pytest.fixture
def logged_in_user(client, user):
    client.force_login(user)
    return user


@pytest.fixture
def another_scm_service():
    scm_service = models.SCMService(scm_service_type="bitbucket", server_url="www.bitbucket.com")
    with username_on_model(models.SCMService, "initial"):
        scm_service.save()

    return scm_service


@pytest.fixture
def an_scm_service():
    scm_service = models.SCMService(scm_service_type="bitbucket", server_url="www.example.com")
    with username_on_model(models.SCMService, "initial"):
        scm_service.save()

    return scm_service


@pytest.fixture
def deactivated_scm_service():
    scm_service = models.SCMService(scm_service_type="bitbucket 2", server_url="www.example.org")
    scm_service.deleted = True
    with username_on_model(models.SCMService, "initial"):
        scm_service.save()

    return scm_service


@pytest.fixture
def scm_service(an_scm_service, another_scm_service, deactivated_scm_service):
    return an_scm_service


@pytest.fixture
def not_my_scm_repository(scm_service, not_my_credential):
    scm_repository = models.SCMRepository(
        scm_service=scm_service, credential=not_my_credential, organisation="acme", repository_name="not-mine"
    )
    with username_on_model(models.SCMRepository, "initial"):
        scm_repository.save()

    return scm_repository


@pytest.fixture
def my_scm_repository(scm_service, credential, not_my_scm_repository):
    scm_repository = models.SCMRepository(
        scm_service=scm_service, credential=credential, organisation="acme", repository_name="sample"
    )
    with username_on_model(models.SCMRepository, "initial"):
        scm_repository.save()

    return scm_repository


@pytest.fixture
def my_other_scm_repository(another_scm_service, my_other_teams_credential):
    scm_repository = models.SCMRepository(
        scm_service=another_scm_service,
        credential=my_other_teams_credential,
        organisation="acme",
        repository_name="another",
    )
    with username_on_model(models.SCMRepository, "initial"):
        scm_repository.save()

    return scm_repository


@pytest.fixture
def deactivated_scm_repository(scm_service, credential):
    scm_repository = models.SCMRepository(
        scm_service=scm_service, credential=credential, organisation="acme", repository_name="example"
    )
    scm_repository.deleted = True
    with username_on_model(models.SCMRepository, "initial"):
        scm_repository.save()

    return scm_repository


@pytest.fixture
def scm_repository(my_scm_repository, my_other_scm_repository, not_my_scm_repository, deactivated_scm_repository):
    return my_scm_repository


@pytest.fixture
def not_my_application(not_my_project, not_my_scm_repository):
    application = models.Application(
        project=not_my_project, scm_repository=not_my_scm_repository, name="Application Not mine", slug="APPNO"
    )
    with username_on_model(models.Application, "initial"):
        application.save()

    return application


@pytest.fixture
def my_application(project, scm_repository, not_my_application):
    application = models.Application(project=project, scm_repository=scm_repository, name="Application D", slug="APPD")
    with username_on_model(models.Application, "initial"):
        application.save()

    return application


@pytest.fixture
def my_other_application(my_other_project, my_other_scm_repository):
    application = models.Application(
        project=my_other_project, scm_repository=my_other_scm_repository, name="Application 2", slug="APP2"
    )
    with username_on_model(models.Application, "initial"):
        application.save()

    return application


@pytest.fixture
def deactivated_application(project, deactivated_scm_repository):
    application = models.Application(
        project=project, scm_repository=deactivated_scm_repository, name="Application Deactivated", slug="APPDeac"
    )
    application.deleted = True
    with username_on_model(models.Application, "initial"):
        application.save()

    return application


@pytest.fixture
def application(my_application, my_other_application, not_my_application, deactivated_application):
    return my_application


@pytest.fixture
def not_my_scm_pipeline_run(not_my_application):
    scm_pipeline_run = models.SCMPipelineRun(
        application=not_my_application,
        pipeline_yaml="---",
        steps_total=5,
        commit_hash="8875B57A143AEC5156FD1444A017A32137A3F321",
    )
    with username_on_model(models.SCMPipelineRun, "initial"):
        scm_pipeline_run.save()

    return scm_pipeline_run


@pytest.fixture
def my_scm_pipeline_run(application):
    pipeline_yaml = """stages:
  - release

do-release:
  stage: release
"""
    scm_pipeline_run = models.SCMPipelineRun(
        application=application,
        pipeline_yaml=pipeline_yaml,
        steps_total=5,
        commit_hash="4015B57A143AEC5156FD1444A017A32137A3FD0F",
    )
    with username_on_model(models.SCMPipelineRun, "initial"):
        scm_pipeline_run.save()

    return scm_pipeline_run


@pytest.fixture
def next_scm_pipeline_run(application, my_scm_pipeline_run):
    pipeline_yaml = """stages:
  - release

do-release:
  stage: release
"""
    scm_pipeline_run = models.SCMPipelineRun(
        application=application,
        pipeline_yaml=pipeline_yaml,
        steps_total=5,
        commit_hash="DD14567A143AEC5156FD1444A017A3213654EF1",
        first_parent_hash=my_scm_pipeline_run.commit_hash,
    )
    with username_on_model(models.SCMPipelineRun, "initial"):
        scm_pipeline_run.save()

    return scm_pipeline_run


@pytest.fixture
def another_scm_pipeline_run(my_other_application):
    pipeline_yaml = """stages:
  - release

do-release:
  stage: release
"""
    scm_pipeline_run = models.SCMPipelineRun(
        application=my_other_application,
        pipeline_yaml=pipeline_yaml,
        steps_total=5,
        commit_hash="1234567A143AEC5156FD1444A017A3213654321",
    )
    with username_on_model(models.SCMPipelineRun, "initial"):
        scm_pipeline_run.save()

    return scm_pipeline_run


@pytest.fixture
def another_another_scm_pipeline_run(my_other_application):
    pipeline_yaml = """stages:
  - release

do-release:
  stage: release
"""
    scm_pipeline_run = models.SCMPipelineRun(
        application=my_other_application,
        pipeline_yaml=pipeline_yaml,
        steps_total=5,
        commit_hash="9234567A143AEC5156FD1444A017A3213654329",
        # first_parent_hash does not link to existing hash
        first_parent_hash="40000000000000000000000000000000000000F",
    )
    with username_on_model(models.SCMPipelineRun, "initial"):
        scm_pipeline_run.save()

    return scm_pipeline_run


@pytest.fixture
def different_scm_pipeline_run(my_other_application):
    pipeline_yaml = """stages:
  - release

do-release:
  stage: release
"""
    scm_pipeline_run = models.SCMPipelineRun(
        application=my_other_application,
        pipeline_yaml=pipeline_yaml,
        steps_total=5,
        commit_hash="9234567A143AEC5156FD1444A017A3213654321",
        # first_parent_hash does not link to existing hash
        first_parent_hash="40000000000000000000000000000000000000F",
    )
    with username_on_model(models.SCMPipelineRun, "initial"):
        scm_pipeline_run.save()

    return scm_pipeline_run


@pytest.fixture
def deactivated_scm_pipeline_run(application):
    scm_pipeline_run = models.SCMPipelineRun(
        application=application,
        pipeline_yaml="---",
        steps_total=5,
        commit_hash="8975B57A143AEC5156FD1444A017A32137A3FBA3",
    )
    scm_pipeline_run.deleted = True
    with username_on_model(models.SCMPipelineRun, "initial"):
        scm_pipeline_run.save()

    return scm_pipeline_run


@pytest.fixture
def scm_pipeline_run(
    my_scm_pipeline_run,
    next_scm_pipeline_run,
    not_my_scm_pipeline_run,
    another_scm_pipeline_run,
    another_another_scm_pipeline_run,
    deactivated_scm_pipeline_run,
):
    return my_scm_pipeline_run


@pytest.fixture
def not_my_scm_step_run(not_my_scm_pipeline_run):
    scm_step_run = models.SCMStepRun(
        slug="another-release",
        name="Another Release Katka",
        stage="Production",
        scm_pipeline_run=not_my_scm_pipeline_run,
    )

    with username_on_model(models.SCMStepRun, "initial"):
        scm_step_run.save()

    return scm_step_run


@pytest.fixture
def my_scm_step_run(my_scm_pipeline_run):
    scm_step_run = models.SCMStepRun(
        slug="release",
        name="Release Katka",
        stage="Production",
        step_type="type",
        scm_pipeline_run=my_scm_pipeline_run,
        sequence_id="1.1-1",
        started_at="2018-11-11 08:25:30+0000",
        ended_at="2018-11-11 09:01:40+0000",
    )

    with username_on_model(models.SCMStepRun, "initial"):
        scm_step_run.save()

    return scm_step_run


@pytest.fixture
def another_scm_step_run(another_scm_pipeline_run):
    scm_step_run = models.SCMStepRun(
        slug="another-release",
        name="Another Release Katka",
        stage="Production",
        scm_pipeline_run=another_scm_pipeline_run,
    )

    with username_on_model(models.SCMStepRun, "initial"):
        scm_step_run.save()

    return scm_step_run


@pytest.fixture
def deactivated_scm_step_run(my_scm_pipeline_run):
    scm_step_run = models.SCMStepRun(
        slug="another-release", name="Another Release Katka", stage="Production", scm_pipeline_run=my_scm_pipeline_run,
    )
    scm_step_run.deleted = True
    with username_on_model(models.SCMStepRun, "initial"):
        scm_step_run.save()

    return scm_step_run


@pytest.fixture
def scm_step_run(not_my_scm_step_run, my_scm_step_run, another_scm_step_run, deactivated_scm_step_run):
    return my_scm_step_run


@pytest.fixture
def not_my_scm_release(not_my_scm_pipeline_run):

    with username_on_model(models.SCMRelease, "initial"):
        scm_release = models.SCMRelease.objects.create()
        scm_release.scm_pipeline_runs.add(not_my_scm_pipeline_run)
        scm_release.name = "Version 1.2.1"
        scm_release.save()

    return scm_release


@pytest.fixture
def my_scm_release(my_scm_pipeline_run):

    with username_on_model(models.SCMRelease, "initial"):
        scm_release = models.SCMRelease.objects.create()
        scm_release.scm_pipeline_runs.add(my_scm_pipeline_run)
        scm_release.name = "Version 0.13.1"
        scm_release.save()

    return scm_release


@pytest.fixture
def deactivated_scm_release(deactivated_scm_pipeline_run):
    scm_release = models.SCMRelease()
    scm_release.deleted = True
    with username_on_model(models.SCMRelease, "initial"):
        scm_release.save()

    return scm_release


@pytest.fixture
def another_scm_release(another_scm_pipeline_run):

    with username_on_model(models.SCMRelease, "initial"):
        scm_release = models.SCMRelease.objects.create()
        scm_release.scm_pipeline_runs.add(another_scm_pipeline_run)
        scm_release.name = "Version 15.0"
        scm_release.save()

    return scm_release


@pytest.fixture
def scm_release_with_multi_pipelines(different_scm_pipeline_run, another_scm_pipeline_run):
    with username_on_model(models.SCMRelease, "initial"):
        scm_release = models.SCMRelease.objects.create()
        scm_release.scm_pipeline_runs.add(another_scm_pipeline_run)
        scm_release.scm_pipeline_runs.add(different_scm_pipeline_run)
        scm_release.name = "Version 16.0"
        scm_release.save()
    return scm_release


@pytest.fixture
def scm_releases_with_multi_pipeline_runs(another_scm_pipeline_run, another_another_scm_pipeline_run):

    with username_on_model(models.SCMRelease, "initial"):
        scm_release = models.SCMRelease.objects.create()
        scm_release.scm_pipeline_runs.add(another_scm_pipeline_run)
        scm_release.scm_pipeline_runs.add(another_another_scm_pipeline_run)
        scm_release.name = "New"
        scm_release.save()

    return scm_release


@pytest.fixture
def multiple_scm_releases(another_scm_pipeline_run, another_another_scm_pipeline_run, different_scm_pipeline_run):
    # I want to make sure they are created in sequence
    with username_on_model(models.SCMRelease, "initial"):
        scm_release = models.SCMRelease.objects.create()
        scm_release.scm_pipeline_runs.add(another_scm_pipeline_run)
        scm_release.name = "Old"
        scm_release.save()

        scm_release = models.SCMRelease.objects.create()
        scm_release.scm_pipeline_runs.add(another_another_scm_pipeline_run)
        scm_release.scm_pipeline_runs.add(different_scm_pipeline_run)
        scm_release.name = "New"
        scm_release.save()

    return scm_release


@pytest.fixture
def scm_release(my_scm_release, another_scm_release, deactivated_scm_release, not_my_scm_release):
    return my_scm_release


@pytest.fixture
def my_metadata(my_application):
    meta = models.ApplicationMetadata(key="ci", value="the-team", application=my_application)
    with username_on_model(models.ApplicationMetadata, "initial"):
        meta.save()

    return meta


@pytest.fixture
def deactivated_metadata(deactivated_application):
    metadata = models.ApplicationMetadata(key="ci", value="the-team-2", application=deactivated_application)
    metadata.deleted = True
    with username_on_model(models.ApplicationMetadata, "initial"):
        metadata.save()

    return metadata


@pytest.fixture
def not_my_metadata(not_my_application):
    meta = models.ApplicationMetadata(key="ci-not-mine", value="the-team-not-mine", application=not_my_application)
    with username_on_model(models.ApplicationMetadata, "initial"):
        meta.save()

    return meta


@pytest.fixture
def metadata(my_metadata, not_my_metadata, deactivated_metadata):
    return my_metadata


@pytest.fixture
def most_models(
    application,
    credential,
    metadata,
    project,
    secret,
    scm_pipeline_run,
    scm_repository,
    scm_release,
    scm_service,
    scm_step_run,
    team,
    user,
    not_my_application,
    not_my_credential,
    not_my_metadata,
    not_my_scm_pipeline_run,
    not_my_project,
    not_my_scm_repository,
    not_my_scm_release,
    not_my_secret,
    not_my_scm_step_run,
    not_my_team,
):
    return {
        "application": application,
        "credential": credential,
        "metadata": metadata,
        "pipeline_run": scm_pipeline_run,
        "project": project,
        "repository": scm_repository,
        "release": scm_release,
        "secret": secret,
        "service": scm_service,
        "step_run": scm_step_run,
        "team": team,
        "user": user,
        "not_my_application": not_my_application,
        "not_my_credential": not_my_credential,
        "not_my_metadata": not_my_metadata,
        "not_my_pipeline_run": not_my_scm_pipeline_run,
        "not_my_project": not_my_project,
        "not_my_repository": not_my_scm_repository,
        "not_my_release": not_my_scm_release,
        "not_my_secret": not_my_secret,
        "not_my_step_run": not_my_scm_step_run,
        "not_my_team": not_my_team,
    }
