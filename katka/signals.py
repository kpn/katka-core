import logging
from urllib.parse import urljoin

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from katka.constants import (
    PIPELINE_STATUS_FAILED,
    PIPELINE_STATUS_IN_PROGRESS,
    PIPELINE_STATUS_INITIALIZING,
    PIPELINE_STATUS_QUEUED,
    PIPELINE_STATUS_SKIPPED,
    STEP_FINAL_STATUSES,
)
from katka.fields import username_on_model
from katka.models import SCMPipelineRun, SCMStepRun
from katka.releases import close_release_if_pipeline_finished, create_release_if_necessary
from requests import HTTPError

log = logging.getLogger("katka")


@receiver(post_save, sender=SCMStepRun)
def update_pipeline_from_steps(sender, **kwargs):
    """
    Update the pipeline 'steps_completed' and 'steps_total' in case they changed whenever a step is updated/added
    """
    pipeline = kwargs["instance"].scm_pipeline_run
    pipeline_steps = SCMStepRun.objects.filter(scm_pipeline_run=pipeline)

    before_steps_total = pipeline.steps_total
    before_steps_completed = pipeline.steps_completed

    pipeline.steps_total = pipeline_steps.count()
    pipeline.steps_completed = pipeline_steps.filter(status__in=STEP_FINAL_STATUSES).count()

    if pipeline.steps_completed != before_steps_completed or pipeline.steps_total != before_steps_total:
        with username_on_model(SCMPipelineRun, kwargs["instance"].modified_username):
            pipeline.save()


@receiver(post_save, sender=SCMPipelineRun)
def send_pipeline_change_notification(sender, **kwargs):
    pipeline = kwargs["instance"]
    if pipeline.status == PIPELINE_STATUS_INITIALIZING and kwargs["created"] is False:
        # Do not send notifications when the pipeline is initializing. While initializing, steps are created and
        # since this is done with several requests, several notifications would be sent, while the only one you
        # care about is when all the steps are created and the status is changed to 'in progress'.
        # There is one exception though, a notify *should* be sent when the pipeline is first created, because
        # the notification will trigger the creation of the steps.
        return

    if pipeline.status == PIPELINE_STATUS_QUEUED:
        # When a pipeline is queued it means that other pipelines should be run first. To prevent them from
        # being run, do not notify.
        return

    session = settings.PIPELINE_RUNNER_SESSION
    url = urljoin(settings.PIPELINE_RUNNER_BASE_URL, settings.PIPELINE_CHANGE_NOTIFICATION_EP)
    response = session.post(url, json={"public_identifier": str(pipeline.public_identifier)})

    try:
        response.raise_for_status()
    except HTTPError:
        log.exception("Failed to notify pipeline runner")


@receiver(post_save, sender=SCMPipelineRun)
def create_close_releases(sender, **kwargs):
    pipeline = kwargs["instance"]
    if pipeline.status == PIPELINE_STATUS_SKIPPED:
        return

    if pipeline.status == PIPELINE_STATUS_FAILED:
        # it could be that the pipeline will never be in progress due to error in the
        # initialization, which as a side effect will let the pipeline without any release.
        # So, we check explicitly here to make sure we don't mess up with the workflow from
        # `close_release_if_pipeline_finished`
        create_release_if_necessary(pipeline)

    if pipeline.status == PIPELINE_STATUS_IN_PROGRESS:
        create_release_if_necessary(pipeline)
    else:
        close_release_if_pipeline_finished(pipeline)
