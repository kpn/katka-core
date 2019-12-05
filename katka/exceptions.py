from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException


class MissingUsername(Exception):
    pass


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _("Conflict.")
    default_code = "conflict"


class AlreadyExists(Conflict):
    default_detail = {"detail": "Object already exists.", "code": "already_exists"}
    default_code = "already_exists"


class ParentCommitMissing(Conflict):
    default_detail = {
        "detail": "Pipeline Run could not be created, no pipeline run found for parent commit hash.",
        "code": "parent_commit_missing",
    }
    default_code = "parent_commit_missing"
