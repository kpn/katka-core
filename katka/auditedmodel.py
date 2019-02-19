from django.db import models

from katka.fields import AutoUsernameField


class AuditedModel(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True, editable=False)
    created_username = AutoUsernameField(only_on_create=True)
    modified = models.DateTimeField(auto_now=True, editable=False)
    modified_username = AutoUsernameField()
    deleted = models.BooleanField(default=False)
