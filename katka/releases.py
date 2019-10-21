import logging
from dataclasses import dataclass

from katka import constants
from katka.fields import username_on_model
from katka.models import SCMPipelineRun, SCMRelease, SCMStepRun

log = logging.getLogger('katka')


@dataclass
class StepsPreConditions:
    start_tag_executed: bool
    end_tag_executed: bool
    success_status_between_start_end: list

    @property
    def all_status_between_start_and_finish_are_success(self):
        return all(self.success_status_between_start_end)

    @property
    def start_and_finish_tags_were_executed(self):
        return self.start_tag_executed and self.end_tag_executed


def create_release_if_necessary(pipeline):
    release = _get_current_release(pipeline)
    with username_on_model(SCMRelease, pipeline.modified_username):
        if release is None:
            release = SCMRelease.objects.create()

        release.scm_pipeline_runs.add(pipeline)
        release.save()


def close_release_if_pipeline_finished(pipeline: SCMPipelineRun):
    if pipeline.status not in constants.PIPELINE_FINAL_STATUSES:
        log.debug(f'Pipeline {pipeline.public_identifier} not finished, doing nothing')
        return None

    pre_conditions = _gather_steps_pre_conditions(pipeline)
    if not pre_conditions.start_and_finish_tags_were_executed:
        log.debug(f'Pipeline {pipeline.public_identifier} missing start and/or finish tags')
        return None

    release = _get_current_release(pipeline)
    if release and pre_conditions.all_status_between_start_and_finish_are_success:
        release.status = constants.RELEASE_STATUS_SUCCESS
    elif release:
        log.debug(f'Pipeline {pipeline.public_identifier} contains step(s) with failed status')
        release.status = constants.RELEASE_STATUS_FAILED
    else:
        log.warning(f'No open release for pipeline {pipeline.public_identifier}')

    with username_on_model(SCMRelease, pipeline.modified_username):
        if release:
            release.save()

    return release.status if release else None


def _gather_steps_pre_conditions(pipeline):
    steps = SCMStepRun.objects.filter(scm_pipeline_run=pipeline).order_by("sequence_id")
    is_start_tag_executed = False
    is_end_tag_executed = False
    success_status_between_start_end = []
    for step in steps:
        if step.status not in constants.STEP_EXECUTED_STATUSES:
            continue
        if constants.TAG_PRODUCTION_CHANGE_STARTED in step.tags.split(" "):
            is_start_tag_executed = True

        if is_start_tag_executed:
            success_status_between_start_end.append(step.status == constants.STEP_STATUS_SUCCESS)

        if constants.TAG_PRODUCTION_CHANGE_ENDED in step.tags.split(" "):
            is_end_tag_executed = True
            break

    return StepsPreConditions(is_start_tag_executed, is_end_tag_executed, success_status_between_start_end)


def _get_current_release(pipeline):
    releases = SCMRelease.objects.filter(
        status=constants.RELEASE_STATUS_IN_PROGRESS, scm_pipeline_runs__application=pipeline.application
    )
    release = None
    if len(releases) == 0:
        log.error(f'No open releases found for application {pipeline.application.pk}')
    elif len(releases) > 1:
        log.error(f'Multiple open releases found for application {pipeline.application.pk}, picking newest')
        release = releases.order_by('-created').first()
    else:
        release = releases[0]
    return release
