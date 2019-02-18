from django.db import models

from katka.fields import AutoUsernameField


class AlwaysUpdate(models.Model):
    field = AutoUsernameField()


class OnlyOnCreate(models.Model):
    field = AutoUsernameField(only_on_create=True)
