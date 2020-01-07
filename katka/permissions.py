from katka.auth import AuthType, has_full_access_scope
from rest_framework.permissions import BasePermission, IsAuthenticated


class IsGroupAuthenticated(IsAuthenticated):
    """
    Only if the request has a non anonymous User object and if that user is authenticated, allow
    """

    def has_permission(self, request, view):
        if request.katka_auth_type is not AuthType.GROUPS:
            return False

        return super().has_permission(request, view)


class HasFullScope(BasePermission):
    """
    Only if the request has scopes and if the full_access scope is present, allow
    """

    def has_permission(self, request, view):
        return has_full_access_scope(request)
