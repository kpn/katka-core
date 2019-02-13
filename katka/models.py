import uuid

from django.contrib.auth.models import Group
from django.db import models

from encrypted_model_fields.fields import EncryptedCharField
from katka.auditedmodel import AuditedModel
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
    slug = KatkaSlugField()
    name = models.CharField(max_length=100)
    credential_type = models.CharField(max_length=50)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('team', 'slug')

    def __str__(self):  # pragma: no cover
        return f'{self.name}'


class CredentialSecret(AuditedModel):
    key = models.CharField(max_length=50)
    value = EncryptedCharField(max_length=200)
    credential = models.ForeignKey(Credential, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('credential', 'key')

    def __str__(self):  # pragma: no cover
        return f'{self.credential.name}/{self.key}'
