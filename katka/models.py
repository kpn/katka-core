import uuid

from django.contrib.auth.models import Group
from django.db import models

from encrypted_model_fields.fields import EncryptedCharField
from katka.auditedmodel import AuditedModel
from katka.constants import (
    PIPELINE_STATUS_CHOICES, PIPELINE_STATUS_INITIALIZING, STEP_STATUS_CHOICES, STEP_STATUS_NOT_STARTED,
)
from katka.fields import KatkaSlugField


class Team(AuditedModel):
    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = KatkaSlugField(unique=True)
    name = models.CharField(max_length=100)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):  # pragma: no cover
        return f'{self.group.name}'


class Project(AuditedModel):
    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = KatkaSlugField()
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('team', 'slug')

    def __str__(self):  # pragma: no cover
        return f'{self.name}'


class Credential(AuditedModel):
    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    credential_type = models.CharField(max_length=50)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):  # pragma: no cover
        return f'{self.credential_type}/{self.name}'


class CredentialSecret(AuditedModel):
    key = models.CharField(max_length=50)
    value = EncryptedCharField(max_length=200)
    credential = models.ForeignKey(Credential, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('credential', 'key')

    def __str__(self):  # pragma: no cover
        return f'{self.credential.name}/{self.key}'


class SCMService(AuditedModel):

    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scm_service_type = models.CharField(max_length=48)
    server_url = models.URLField(null=False)

    def __str__(self):  # pragma: no cover
        return f'{self.scm_service_type}/{self.server_url}'


class SCMRepository(AuditedModel):

    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.CharField(max_length=128)
    repository_name = models.CharField(max_length=128)
    credential = models.ForeignKey(Credential, on_delete=models.PROTECT)
    scm_service = models.ForeignKey(SCMService, on_delete=models.PROTECT)

    def __str__(self):  # pragma: no cover
        return f'{self.organisation}/{self.repository_name}'


class Application(AuditedModel):
    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = KatkaSlugField()
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    scm_repository = models.OneToOneField(SCMRepository, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('project', 'slug')

    def __str__(self):  # pragma: no cover
        return f'{self.name}'


# Pipeline run results
class SCMPipelineRun(AuditedModel):
    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    commit_hash = models.CharField(max_length=64)  # A SHA-1 hash is 40 characters, SHA-256 is 64 characters
    status = models.CharField(max_length=30, choices=PIPELINE_STATUS_CHOICES, default=PIPELINE_STATUS_INITIALIZING)
    steps_total = models.PositiveSmallIntegerField()
    steps_completed = models.PositiveSmallIntegerField(default=0)
    pipeline_yaml = models.TextField()
    application = models.ForeignKey(Application, on_delete=models.PROTECT)


class SCMStepRun(AuditedModel):
    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = KatkaSlugField(max_length=30)
    name = models.CharField(max_length=100)
    stage = models.CharField(max_length=100)
    status = models.CharField(max_length=30, choices=STEP_STATUS_CHOICES, default=STEP_STATUS_NOT_STARTED)
    output = models.TextField(blank=True)
    scm_pipeline_run = models.ForeignKey(SCMPipelineRun, on_delete=models.PROTECT)


# SCM Releases, comprises a range of commits that are released
class SCMRelease(AuditedModel):
    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    released = models.DateTimeField(null=True)
    from_hash = models.CharField(max_length=64)
    to_hash = models.CharField(max_length=64)
    # points to the pipeline run that created the release, and contains the information on the deployment pipeline
    scm_pipeline_run = models.ForeignKey(SCMPipelineRun, on_delete=models.PROTECT)
