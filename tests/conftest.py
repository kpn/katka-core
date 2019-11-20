from django.contrib.auth.models import Group, User

import pytest
from katka import models
from katka.fields import username_on_model


@pytest.fixture
def group():
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
def not_my_team(not_my_group):
    z_team = models.Team(name="Z-Team", slug="ZTM", group=not_my_group)

    with username_on_model(models.Team, "initial"):
        z_team.save()

    return z_team


@pytest.fixture
def my_team(group):
    a_team = models.Team(name="A-Team", slug="ATM", group=group)

    with username_on_model(models.Team, "initial"):
        a_team.save()

    return a_team


@pytest.fixture
def team(my_team, not_my_team):
    """Return my team, but also make sure that 'not_my_team' is active so we can test if it is excluded, etc."""
    return my_team


@pytest.fixture
def my_other_team(my_other_group):
    a_team = models.Team(name="B-Team", slug="BTM", group=my_other_group)

    with username_on_model(models.Team, "initial"):
        a_team.save()

    return a_team


@pytest.fixture
def deactivated_team(team):
    team.deleted = True
    with username_on_model(models.Team, "deactivator"):
        team.save()

    return team


@pytest.fixture
def project(team):
    project = models.Project(team=team, name="Project D", slug="PRJD")
    with username_on_model(models.Project, "initial"):
        project.save()

    return project


@pytest.fixture
def not_my_project(not_my_team):
    project = models.Project(team=not_my_team, name="Project Not Mine", slug="NMP1")
    with username_on_model(models.Project, "initial"):
        project.save()

    return project


@pytest.fixture
def another_project(my_other_team):
    project = models.Project(team=my_other_team, name="Project 2", slug="PRJ2")
    with username_on_model(models.Project, "initial"):
        project.save()

    return project


@pytest.fixture
def deactivated_project(team, project):
    project.deleted = True
    with username_on_model(models.Project, "initial"):
        project.save()

    return project


@pytest.fixture
def my_credential(team):
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
def not_my_credential(not_my_team):
    credential = models.Credential(name="System user D", team=not_my_team)
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
def my_secret(credential):
    secret = models.CredentialSecret(key="access_token", value="full_access_value", credential=credential)
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
def not_my_secret(not_my_credential):
    secret = models.CredentialSecret(key="access_token", value="full_access_value", credential=not_my_credential)
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
def scm_service():
    scm_service = models.SCMService(scm_service_type="bitbucket", server_url="www.example.com")
    with username_on_model(models.SCMService, "initial"):
        scm_service.save()

    return scm_service


@pytest.fixture
def another_scm_service():
    scm_service = models.SCMService(scm_service_type="bitbucket", server_url="www.bitbucket.com")
    with username_on_model(models.SCMService, "initial"):
        scm_service.save()

    return scm_service


@pytest.fixture
def deactivated_scm_service(scm_service):
    scm_service.deleted = True
    with username_on_model(models.SCMService, "initial"):
        scm_service.save()

    return scm_service


@pytest.fixture
def scm_repository(scm_service, credential):
    scm_repository = models.SCMRepository(
        scm_service=scm_service, credential=credential, organisation="acme", repository_name="sample"
    )
    with username_on_model(models.SCMRepository, "initial"):
        scm_repository.save()

    return scm_repository


@pytest.fixture
def another_scm_repository(another_scm_service, my_other_teams_credential):
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
def deactivated_scm_repository(scm_repository):
    scm_repository.deleted = True
    with username_on_model(models.SCMRepository, "initial"):
        scm_repository.save()

    return scm_repository


@pytest.fixture
def application(project, scm_repository):
    application = models.Application(project=project, scm_repository=scm_repository, name="Application D", slug="APPD")
    with username_on_model(models.Application, "initial"):
        application.save()

    return application


@pytest.fixture
def another_application(another_project, another_scm_repository):
    application = models.Application(
        project=another_project, scm_repository=another_scm_repository, name="Application 2", slug="APP2"
    )
    with username_on_model(models.Application, "initial"):
        application.save()

    return application


@pytest.fixture
def deactivated_application(application):
    application.deleted = True
    with username_on_model(models.Application, "initial"):
        application.save()

    return application


@pytest.fixture
def scm_pipeline_run(application):
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
def next_scm_pipeline_run(application, scm_pipeline_run):
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
        first_parent_hash=scm_pipeline_run.commit_hash,
    )
    with username_on_model(models.SCMPipelineRun, "initial"):
        scm_pipeline_run.save()

    return scm_pipeline_run


@pytest.fixture
def another_scm_pipeline_run(another_application):
    pipeline_yaml = """stages:
  - release

do-release:
  stage: release
"""
    scm_pipeline_run = models.SCMPipelineRun(
        application=another_application,
        pipeline_yaml=pipeline_yaml,
        steps_total=5,
        commit_hash="1234567A143AEC5156FD1444A017A3213654321",
    )
    with username_on_model(models.SCMPipelineRun, "initial"):
        scm_pipeline_run.save()

    return scm_pipeline_run


@pytest.fixture
def another_another_scm_pipeline_run(another_application):
    pipeline_yaml = """stages:
  - release

do-release:
  stage: release
"""
    scm_pipeline_run = models.SCMPipelineRun(
        application=another_application,
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
def deactivated_scm_pipeline_run(scm_pipeline_run):
    scm_pipeline_run.deleted = True
    with username_on_model(models.SCMPipelineRun, "initial"):
        scm_pipeline_run.save()

    return scm_pipeline_run


@pytest.fixture
def scm_step_run(scm_pipeline_run):
    scm_step_run = models.SCMStepRun(
        slug="release",
        name="Release Katka",
        stage="Production",
        step_type="type",
        scm_pipeline_run=scm_pipeline_run,
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
def deactivated_scm_step_run(scm_step_run):
    scm_step_run.deleted = True
    with username_on_model(models.SCMStepRun, "initial"):
        scm_step_run.save()

    return scm_step_run


@pytest.fixture
def scm_release(scm_pipeline_run):
    scm_release = models.SCMRelease.objects.filter(scm_pipeline_runs__pk__exact=scm_pipeline_run.pk).first()

    with username_on_model(models.SCMRelease, "initial"):
        scm_release.name = "Version 0.13.1"
        scm_release.save()

    return scm_release


@pytest.fixture
def deactivated_scm_release(scm_release):
    scm_release.deleted = True
    with username_on_model(models.SCMRelease, "initial"):
        scm_release.save()

    return scm_release


@pytest.fixture
def another_scm_release(another_scm_pipeline_run):
    scm_release = models.SCMRelease.objects.filter(scm_pipeline_runs__pk__exact=another_scm_pipeline_run.pk).first()

    with username_on_model(models.SCMRelease, "initial"):
        scm_release.name = "Version 15.0"
        scm_release.save()

    return scm_release


@pytest.fixture
def metadata(application):
    meta = models.ApplicationMetadata(key="ci", value="the-team", application=application)
    with username_on_model(models.ApplicationMetadata, "initial"):
        meta.save()

    return meta


@pytest.fixture
def deactivated_metadata(metadata):
    metadata.deleted = True
    with username_on_model(models.ApplicationMetadata, "initial"):
        metadata.save()

    return metadata


@pytest.fixture
def not_my_application(another_scm_repository, not_my_project):
    application = models.Application(
        project=not_my_project, scm_repository=another_scm_repository, name="Application 98", slug="APP98"
    )
    with username_on_model(models.Application, "initial"):
        application.save()

    return application


@pytest.fixture
def not_my_metadata(not_my_application):
    meta = models.ApplicationMetadata(key="ci-not-mine", value="the-team-not-mine", application=not_my_application)
    with username_on_model(models.ApplicationMetadata, "initial"):
        meta.save()

    return meta


@pytest.fixture
def step_data(scm_pipeline_run):
    version = '{"release.version": "1.0.0"}'
    steps = [
        {
            "name": "step0",
            "stage": "prepare",
            "seq": "1.1-1",
            "status": "success",
            "tags": "",
            "output": version,
            "started_at": "2018-11-11 08:25:30+0000",
            "ended_at": "2018-11-11 08:25:41+0000",
        },
        {
            "name": "step1",
            "stage": "prepare",
            "seq": "1.2-1",
            "status": "success",
            "tags": "",
            "output": "",
            "started_at": "2018-11-11 08:35:30+0000",
            "ended_at": "2018-11-11 08:35:41+0000",
        },
        {
            "name": "step2",
            "stage": "deploy",
            "seq": "2.1-1",
            "status": "success",
            "tags": "",
            "output": "",
            "started_at": "2018-11-11 08:45:30+0000",
            "ended_at": "2018-11-11 08:45:41+0000",
        },
        {
            "name": "step3",
            "stage": "deploy",
            "seq": "2.2-1",
            "status": "success",
            "tags": "",
            "output": "",
            "started_at": "2018-11-11 08:55:30+0000",
            "ended_at": "2018-11-11 08:55:41+0000",
        },
        {
            "name": "step4",
            "stage": "deploy",
            "seq": "2.3-1",
            "status": "success",
            "tags": "",
            "output": "",
            "started_at": "2018-11-11 09:05:30+0000",
            "ended_at": "2018-11-11 09:05:41+0000",
        },
        {
            "name": "step5",
            "stage": "deploy",
            "seq": "2.4-1",
            "status": "success",
            "tags": "",
            "output": "",
            "started_at": "2018-11-11 09:15:30+0000",
            "ended_at": "2018-11-11 09:15:41+0000",
        },
        {
            "name": "step6",
            "stage": "deploy",
            "seq": "2.5-1",
            "status": "success",
            "tags": "",
            "output": "",
            "started_at": "2018-11-11 09:25:30+0000",
            "ended_at": "2018-11-11 09:25:41+0000",
        },
    ]
    return steps


def _create_steps_from_dict(scm_pipeline_run, step_data):
    saved_steps = []
    for step in step_data:
        scm_step_run = models.SCMStepRun(
            slug=step["name"],
            name=step["name"],
            stage=step["stage"],
            scm_pipeline_run=scm_pipeline_run,
            sequence_id=step["seq"],
            status=step["status"],
            tags=step["tags"],
            output=step["output"],
            started_at=step["started_at"],
            ended_at=step["ended_at"],
        )

        with username_on_model(models.SCMStepRun, "initial"):
            scm_step_run.save()
            saved_steps.append(scm_step_run)

    return saved_steps


@pytest.fixture
def scm_step_run_success_list(scm_pipeline_run, step_data):
    return _create_steps_from_dict(scm_pipeline_run, step_data)


@pytest.fixture
def scm_step_run_success_list_with_start_tag(scm_pipeline_run, step_data):
    step_data[2]["tags"] = "production_change_start"
    return _create_steps_from_dict(scm_pipeline_run, step_data)


@pytest.fixture
def scm_step_run_success_list_with_start_end_tags(scm_pipeline_run, step_data):
    step_data[2]["tags"] = "production_change_start"
    step_data[5]["tags"] = "production_change_end"
    return _create_steps_from_dict(scm_pipeline_run, step_data)


@pytest.fixture
def scm_step_run_one_failed_step_list_with_start_end_tags(scm_pipeline_run, step_data):
    step_data[2]["tags"] = "production_change_start"
    step_data[4]["status"] = "failed"
    step_data[5]["tags"] = "production_change_end"
    return _create_steps_from_dict(scm_pipeline_run, step_data)


@pytest.fixture
def scm_step_run_one_failed_step_before_start_tag(scm_pipeline_run, step_data):
    step_data[1]["status"] = "failed"
    step_data[2]["status"] = "skipped"
    step_data[3]["status"] = "skipped"
    step_data[4]["status"] = "skipped"
    step_data[6]["status"] = "skipped"
    step_data[2]["tags"] = "production_change_start"
    step_data[5]["tags"] = "production_change_end"
    return _create_steps_from_dict(scm_pipeline_run, step_data)


@pytest.fixture
def scm_step_run_one_failed_step_after_end_tag(scm_pipeline_run, step_data):
    step_data[2]["tags"] = "production_change_start"
    step_data[5]["tags"] = "production_change_end"
    step_data[6]["status"] = "failed"
    return _create_steps_from_dict(scm_pipeline_run, step_data)


@pytest.fixture
def scm_step_run_without_version_output(scm_pipeline_run, step_data):
    step_data[0]["output"] = ""
    step_data[2]["tags"] = "production_change_start"
    step_data[5]["tags"] = "production_change_end"
    return _create_steps_from_dict(scm_pipeline_run, step_data)


@pytest.fixture
def scm_step_run_with_broken_output(scm_pipeline_run, step_data):
    step_data[2]["output"] = "1:2"
    step_data[2]["tags"] = "production_change_start"
    step_data[5]["tags"] = "production_change_end"
    return _create_steps_from_dict(scm_pipeline_run, step_data)


@pytest.fixture
def scm_pipeline_run_with_no_open_release(
    another_project, another_scm_repository, scm_step_run_success_list_with_start_end_tags
):
    application = models.Application(
        project=another_project, scm_repository=another_scm_repository, name="Application 2", slug="APP2"
    )
    with username_on_model(models.Application, "initial"):
        application.save()

    pipeline_yaml = """stages:
             - release

           do-release:
             stage: release
           """
    scm_pipeline_run = models.SCMPipelineRun(
        application=application,
        pipeline_yaml=pipeline_yaml,
        steps_total=5,
        status="success",
        commit_hash="4015B57A143AEC5156FD1444A017A32137A3FD0F",
    )
    with username_on_model(models.SCMPipelineRun, "initial"):
        scm_pipeline_run.save()

    with username_on_model(models.SCMStepRun, "initial"):
        for step in scm_step_run_success_list_with_start_end_tags:
            step.scm_pipeline_run = scm_pipeline_run
            step.save()

    return scm_pipeline_run
