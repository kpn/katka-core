import json
import logging
from dataclasses import dataclass
from datetime import datetime

from katka import constants
from katka.fields import username_on_model
from katka.models import SCMPipelineRun, SCMRelease, SCMStepRun

log = logging.getLogger("katka")


@dataclass
class StepsPreConditions:
    version_number: str
    success_status_between_start_end: list
    prod_change_start_date: datetime = None
    prod_change_end_date: datetime = None

    @property
    def all_status_between_start_and_finish_are_success(self):
        return all(self.success_status_between_start_end)

    @property
    def start_and_finish_tags_were_executed(self):
        return self.prod_change_start_date is not None and self.prod_change_end_date is not None


def create_release_if_necessary(pipeline):
    release = _get_current_release(pipeline)
    with username_on_model(SCMRelease, pipeline.modified_username):
        if release is None:
            release = SCMRelease.objects.create()

        release.scm_pipeline_runs.add(pipeline)
        release.save()


def close_release_if_pipeline_finished(pipeline: SCMPipelineRun):
    if pipeline.status not in constants.PIPELINE_FINAL_STATUSES:
        log.debug(f"Pipeline {pipeline.public_identifier} not finished, doing nothing")
        return None

    pre_conditions = _gather_steps_pre_conditions(pipeline)
    if not pre_conditions.start_and_finish_tags_were_executed:
        log.debug(f"Pipeline {pipeline.public_identifier} missing start and/or finish tags")
        return None

    if not pre_conditions.version_number:
        log.debug(f"Pipeline {pipeline.public_identifier} missing release version")
        return None

    release = _get_current_release(pipeline)
    if release and pre_conditions.all_status_between_start_and_finish_are_success:
        release.status = constants.RELEASE_STATUS_SUCCESS
    elif release:
        log.debug(f"Pipeline {pipeline.public_identifier} contains step(s) with failed status")
        release.status = constants.RELEASE_STATUS_FAILED
    else:
        log.warning(f"No open release for pipeline {pipeline.public_identifier}")

    with username_on_model(SCMRelease, pipeline.modified_username):
        if release:
            release.name = pre_conditions.version_number
            release.started_at = pre_conditions.prod_change_start_date
            release.ended_at = pre_conditions.prod_change_end_date
            release.save()

    return release.status if release else None


def _gather_steps_pre_conditions(pipeline):
    steps = SCMStepRun.objects.filter(scm_pipeline_run=pipeline).order_by("sequence_id")
    prod_start_date = None
    prod_end_date = None
    success_status_between_start_end = []
    pipeline_output = {}
    for step in steps:
        if step.status not in constants.STEP_EXECUTED_STATUSES:
            continue
        _add_output(pipeline_output=pipeline_output, step_output=step.output)
        if constants.TAG_PRODUCTION_CHANGE_STARTED in step.tags.split(" "):
            prod_start_date = step.started_at

        if prod_start_date is not None:
            success_status_between_start_end.append(step.status == constants.STEP_STATUS_SUCCESS)

        if constants.TAG_PRODUCTION_CHANGE_ENDED in step.tags.split(" "):
            prod_end_date = step.ended_at
            break

    return StepsPreConditions(
        pipeline_output.get("release.version"),
        success_status_between_start_end,
        prod_change_start_date=prod_start_date,
        prod_change_end_date=prod_end_date,
    )


def _add_output(pipeline_output: dict, step_output: str) -> None:
    if not step_output:
        return
    try:
        pipeline_output.update(json.loads(step_output))
    except json.JSONDecodeError:
        log.warning("Invalid JSON in step output")


def _get_current_release(pipeline):
    releases = SCMRelease.objects.filter(
        status=constants.RELEASE_STATUS_IN_PROGRESS, scm_pipeline_runs__application=pipeline.application
    )
    release = None
    if len(releases) == 0:
        log.debug(f"No open releases found for application {pipeline.application.pk}")
    elif len(releases) > 1:
        log.error(f"Multiple open releases found for application {pipeline.application.pk}, picking newest")
        release = releases.order_by("-created_at").first()
    else:
        release = releases[0]
    return release
