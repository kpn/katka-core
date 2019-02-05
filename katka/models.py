import uuid

from django.contrib.auth.models import Group
from django.db import models

from katka.auditedmodel import AuditedModel


class Team(AuditedModel):
    public_identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.group.name}'
