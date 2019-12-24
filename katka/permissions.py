from katka.auth import has_scope
from rest_framework.permissions import BasePermission


class HasFullScope(BasePermission):
    def has_permission(self, request, view):
        return has_scope(request)
