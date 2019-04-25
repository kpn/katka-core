from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .constants import PIPELINE_STATUS_INITIALIZING, STEP_FINAL_STATUSES
from .fields import username_on_model
from .models import SCMPipelineRun, SCMStepRun


@receiver(post_save, sender=SCMStepRun)
def update_pipeline_from_steps(sender, **kwargs):
    """
    Update the pipeline 'steps_completed' and 'steps_total' in case they changed whenever a step is updated/added
    """
    pipeline = kwargs['instance'].scm_pipeline_run
    pipeline_steps = SCMStepRun.objects.filter(scm_pipeline_run=pipeline)

    before_steps_total = pipeline.steps_total
    before_steps_completed = pipeline.steps_completed

    pipeline.steps_total = pipeline_steps.count()
    pipeline.steps_completed = pipeline_steps.filter(status__in=STEP_FINAL_STATUSES).count()

    if pipeline.steps_completed != before_steps_completed or pipeline.steps_total != before_steps_total:
        with username_on_model(SCMPipelineRun, kwargs['instance'].modified_username):
            pipeline.save()


@receiver(post_save, sender=SCMPipelineRun)
def send_pipeline_change_notification(sender, **kwargs):
    pipeline = kwargs['instance']
    if pipeline.status == PIPELINE_STATUS_INITIALIZING:
        # Do not send notifications when the pipeline is initializing. While initializing, steps are created and
        # since this is done with several requests, several notifications would be sent, while the only one you
        # care about is when all the steps are created and the status is changed to 'in progress'.
        return

    session = settings.PIPELINE_CHANGE_NOTIFICATION_SESSION
    session.post(
        settings.PIPELINE_CHANGE_NOTIFICATION_URL, json={'public_identifier': str(pipeline.public_identifier)}
    )
