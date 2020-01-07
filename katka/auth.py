from enum import Enum, auto

from django.conf import settings


class AuthType(Enum):
    ANONYMOUS = auto()
    GROUPS = auto()
    SCOPES = auto()


def has_full_access_scope(request):
    scopes = getattr(request, "scopes", ())
    if getattr(settings, "SCOPE_FULL_ACCESS", None) in scopes:
        return True

    return False
