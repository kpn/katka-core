import uuid

from django.contrib.auth.models import Group
from django.db import models

from encrypted_model_fields.fields import EncryptedCharField
from katka.auditedmodel import AuditedModel
from katka.constants import (
    PIPELINE_STATUS_CHOICES,
    PIPELINE_STATUS_INITIALIZING,
    RELEASE_STATUS_CHOICES,
    RELEASE_STATUS_IN_PROGRESS,
    STEP_STATUS_CHOICES,
    STEP_STATUS_NOT_STARTED,
)
from katka.fields import KatkaSlugField


class Team(AuditedModel):
    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = KatkaSlugField(unique=True)
    name = models.CharField(max_length=100)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):  # pragma: no cover
        return f"{self.group.name}"


class Project(AuditedModel):
    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = KatkaSlugField()
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("team", "slug")

    def __str__(self):  # pragma: no cover
        return f"{self.name}"


class Credential(AuditedModel):
    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    credential_type = models.CharField(max_length=50)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):  # pragma: no cover
        return f"{self.credential_type}/{self.name}"


class CredentialSecret(AuditedModel):
    key = models.CharField(max_length=50)
    value = EncryptedCharField(max_length=200)
    credential = models.ForeignKey(Credential, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("credential", "key")

    def __str__(self):  # pragma: no cover
        return f"{self.credential.name}/{self.key}"


class SCMService(AuditedModel):
    class Meta:
        verbose_name = "SCM service"
        verbose_name_plural = "SCM services"

    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scm_service_type = models.CharField(max_length=48)
    server_url = models.URLField(null=False)

    def __str__(self):  # pragma: no cover
        return f"{self.scm_service_type}/{self.server_url}"


class SCMRepository(AuditedModel):
    class Meta:
        verbose_name = "SCM repository"
        verbose_name_plural = "SCM repositories"

    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.CharField(max_length=128)
    repository_name = models.CharField(max_length=128)
    credential = models.ForeignKey(Credential, on_delete=models.PROTECT)
    scm_service = models.ForeignKey(SCMService, on_delete=models.PROTECT)

    def __str__(self):  # pragma: no cover
        return f"{self.organisation}/{self.repository_name}"


class Application(AuditedModel):
    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = KatkaSlugField()
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    scm_repository = models.OneToOneField(SCMRepository, on_delete=models.PROTECT)

    class Meta:
        unique_together = ("project", "slug")

    def __str__(self):  # pragma: no cover
        return f"{self.name}"


# Pipeline run results
class SCMPipelineRun(AuditedModel):
    class Meta:
        verbose_name = "SCM pipeline"
        verbose_name_plural = "SCM pipelines"
        constraints = (
            models.UniqueConstraint(fields=("commit_hash", "application"), name="unique commits per application"),
        )
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["-created_at"])]

    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    commit_hash = models.CharField(max_length=64)  # A SHA-1 hash is 40 characters, SHA-256 is 64 characters
    first_parent_hash = models.CharField(
        max_length=64,
        help_text="Commit hash of first parent commit, to determine order of commits. First commit has none.",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=30, choices=PIPELINE_STATUS_CHOICES, default=PIPELINE_STATUS_INITIALIZING)
    steps_total = models.PositiveSmallIntegerField(default=0)
    steps_completed = models.PositiveSmallIntegerField(default=0)
    pipeline_yaml = models.TextField(default="---")
    application = models.ForeignKey(Application, on_delete=models.PROTECT)


class SCMStepRun(AuditedModel):
    class Meta:
        verbose_name = "SCM step"
        verbose_name_plural = "SCM steps"

    step_type = models.CharField(max_length=100, null=True)
    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = KatkaSlugField(max_length=30)
    name = models.CharField(max_length=100)
    stage = models.CharField(max_length=100)
    status = models.CharField(max_length=30, choices=STEP_STATUS_CHOICES, default=STEP_STATUS_NOT_STARTED)
    output = models.TextField(blank=True)
    sequence_id = models.CharField(max_length=30, blank=True, null=True)
    # The format of a sequence ID is: <stage_nr>.<step_nr>-<parallel_nr>, with the following explanation:
    #
    #   stage_nr: the sequence number of the stage. The first stage gets number 1, the next 2, then 3, etc.
    #   step_nr: the sequence number of the step inside a stage. Each first step of the stage gets 1, then 2,
    #            then 3, etc.
    #   parallel_nr: these steps can be done in parallel so they only need a sequence so that the interface will show
    #                the steps in a consistent way.
    #
    # an example would be: "1.1-1" or "1.1" if there are no parallel steps. There should be zero padding, so if
    # there are more than 9 stages, it should be "01.1", or if there are more than 9 steps: "1.01".
    # This allows easy sorting for e.g. frontends.
    scm_pipeline_run = models.ForeignKey(SCMPipelineRun, on_delete=models.PROTECT)
    tags = models.TextField(blank=True)
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)


# SCM Releases, comprises a range of commits that are released
class SCMRelease(AuditedModel):
    class Meta:
        verbose_name = "SCM release"
        verbose_name_plural = "SCM releases"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["-created_at"])]

    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=30, choices=RELEASE_STATUS_CHOICES, default=RELEASE_STATUS_IN_PROGRESS)
    started_at = models.DateTimeField(null=True)
    ended_at = models.DateTimeField(null=True)
    scm_pipeline_runs = models.ManyToManyField(SCMPipelineRun)


class ApplicationMetadata(AuditedModel):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=200)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("application", "key")

    def __str__(self):  # pragma: no cover
        return f"{self.application.name}/{self.key}"
