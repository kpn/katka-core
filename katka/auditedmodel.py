from django.db import models

from katka.constants import STATUS_ACTIVE, STATUS_CHOICES
from katka.fields import AutoUsernameField


class AuditedModel(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True, editable=False)
    created_username = AutoUsernameField(only_on_create=True)
    modified = models.DateTimeField(auto_now=True, editable=False)
    modified_username = AutoUsernameField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
