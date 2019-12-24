from django.conf import settings


def has_scope(request):
    scopes = getattr(request, "scopes", ())
    if getattr(settings, "SCOPE_FULL_ACCESS", None) in scopes:
        return True

    return False
