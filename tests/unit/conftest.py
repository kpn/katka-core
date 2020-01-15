import pytest
from katka import models
from katka.fields import username_on_model


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
def group():
    group = models.Group(name="group1")
    group.save()
    return group


@pytest.fixture
def team(group):
    team = models.Team(name="A-Team", slug="ATM", group=group)

    with username_on_model(models.Team, "initial"):
        team.save()

    return team


@pytest.fixture
def project(team):
    project = models.Project(team=team, name="Project D", slug="PRJD")
    with username_on_model(models.Project, "initial"):
        project.save()

    return project


@pytest.fixture
def other_project(team):
    project = models.Project(team=team, name="Project O", slug="PRJO")
    with username_on_model(models.Project, "initial"):
        project.save()

    return project


@pytest.fixture
def scm_service():
    scm_service = models.SCMService(scm_service_type="bitbucket", server_url="www.example.com")
    with username_on_model(models.SCMService, "audit_user"):
        scm_service.save()
    return scm_service


@pytest.fixture
def credential(team):
    credential = models.Credential(name="System user X", team=team)
    with username_on_model(models.Credential, "initial"):
        credential.save()

    return credential


@pytest.fixture
def scm_repository(scm_service, credential):
    scm_repository = models.SCMRepository(
        scm_service=scm_service, credential=credential, organisation="acme", repository_name="sample"
    )
    with username_on_model(models.SCMRepository, "initial"):
        scm_repository.save()

    return scm_repository


@pytest.fixture
def other_scm_repository(scm_service, credential):
    scm_repository = models.SCMRepository(
        scm_service=scm_service, credential=credential, organisation="acme", repository_name="EXAMPLE"
    )
    with username_on_model(models.SCMRepository, "initial"):
        scm_repository.save()

    return scm_repository


@pytest.fixture
def application(project, scm_repository):
    application = models.Application(project=project, scm_repository=scm_repository, name="Application 2", slug="APP2")
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
def scm_release_with_pipeline_run(scm_pipeline_run):
    with username_on_model(models.SCMRelease, "initial"):
        scm_release = models.SCMRelease.objects.create()
        scm_release.scm_pipeline_runs.add(scm_pipeline_run)
        scm_release.name = "Version 15.0"
        scm_release.save()

    return scm_release


@pytest.fixture
def scm_pipeline_run_with_no_open_release(
    application, other_project, other_scm_repository, scm_pipeline_run, scm_step_run_success_list_with_start_end_tags
):
    with username_on_model(models.SCMStepRun, "initial"):
        for step in scm_step_run_success_list_with_start_end_tags:
            step.scm_pipeline_run = scm_pipeline_run
            step.save()

    return scm_pipeline_run
