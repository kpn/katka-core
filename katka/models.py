import uuid

from django.contrib.auth.models import Group
from django.db import models

from katka.auditedmodel import AuditedModel
from katka.fields import KatkaSlugField


class Team(AuditedModel):
    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = KatkaSlugField()
    name = models.CharField(max_length=100)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):  # pragma: no cover
        return f'{self.group.name}'


class Project(AuditedModel):
    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = KatkaSlugField()
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):  # pragma: no cover
        return f'{self.name}'
