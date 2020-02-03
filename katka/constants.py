# Status is not in the model to allow usage in different models
PIPELINE_STATUS_INITIALIZING = "initializing"
PIPELINE_STATUS_QUEUED = "queued"
PIPELINE_STATUS_IN_PROGRESS = "in progress"
PIPELINE_STATUS_FAILED = "failed"
PIPELINE_STATUS_SUCCESS = "success"
PIPELINE_STATUS_SKIPPED = "skipped"

PIPELINE_STATUS_CHOICES = (
    (PIPELINE_STATUS_INITIALIZING, PIPELINE_STATUS_INITIALIZING),
    (PIPELINE_STATUS_QUEUED, PIPELINE_STATUS_QUEUED),
    (PIPELINE_STATUS_IN_PROGRESS, PIPELINE_STATUS_IN_PROGRESS),
    (PIPELINE_STATUS_FAILED, PIPELINE_STATUS_FAILED),
    (PIPELINE_STATUS_SUCCESS, PIPELINE_STATUS_SUCCESS),
    (PIPELINE_STATUS_SKIPPED, PIPELINE_STATUS_SKIPPED),
)

PIPELINE_FINAL_STATUSES = (
    PIPELINE_STATUS_SUCCESS,
    PIPELINE_STATUS_FAILED,
    PIPELINE_STATUS_SKIPPED,
)

STEP_STATUS_NOT_STARTED = "not started"
STEP_STATUS_IN_PROGRESS = "in progress"
STEP_STATUS_WAITING = "waiting"  # A step cannot proceed until some action is completed
STEP_STATUS_SKIPPED = "skipped"  # A step is skipped due to some conditional
STEP_STATUS_ABORTED = "aborted"  # A step was manually aborted
STEP_STATUS_FAILED = "failed"
STEP_STATUS_SUCCESS = "success"

STEP_STATUS_CHOICES = (
    (STEP_STATUS_NOT_STARTED, STEP_STATUS_NOT_STARTED),
    (STEP_STATUS_IN_PROGRESS, STEP_STATUS_IN_PROGRESS),
    (STEP_STATUS_WAITING, STEP_STATUS_WAITING),
    (STEP_STATUS_SKIPPED, STEP_STATUS_SKIPPED),
    (STEP_STATUS_ABORTED, STEP_STATUS_ABORTED),
    (STEP_STATUS_FAILED, STEP_STATUS_FAILED),
    (STEP_STATUS_SUCCESS, STEP_STATUS_SUCCESS),
)

STEP_FINAL_STATUSES = (STEP_STATUS_SKIPPED, STEP_STATUS_FAILED, STEP_STATUS_SUCCESS)
STEP_EXECUTED_STATUSES = (STEP_STATUS_FAILED, STEP_STATUS_SUCCESS)


RELEASE_STATUS_IN_PROGRESS = "in progress"
RELEASE_STATUS_FAILED = "failed"
RELEASE_STATUS_SUCCESS = "success"

RELEASE_STATUS_CHOICES = (
    (RELEASE_STATUS_IN_PROGRESS, RELEASE_STATUS_IN_PROGRESS),
    (RELEASE_STATUS_FAILED, RELEASE_STATUS_FAILED),
    (RELEASE_STATUS_SUCCESS, RELEASE_STATUS_SUCCESS),
)

TAG_PRODUCTION_CHANGE_STARTED = "production_change_start"
TAG_PRODUCTION_CHANGE_ENDED = "production_change_end"
