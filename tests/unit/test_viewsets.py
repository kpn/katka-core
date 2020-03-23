from unittest import mock

from django.http import HttpRequest
from django.test import override_settings

import pytest
from katka.auth import AuthType
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from tests.unit.viewsets import ViewSet


@pytest.fixture
def django_request():
    req = HttpRequest()
    req.method = "OPTIONS"
    req.user = mock.Mock()
    req.user.is_authenticated = False
    req.user.is_anonymous = True
    return req


class TestPerformAuthentication:
    def test_anonymous(self, django_request):
        request = Request(django_request)
        vs = ViewSet(django_request, None)
        vs.perform_authentication(request)

        assert request.katka_auth_type == AuthType.ANONYMOUS
        assert request.katka_user_identifier == "anonymous"

    def test_user(self, django_request):
        django_request.user.is_authenticated = True
        django_request.user.is_anonymous = False
        django_request.user.username = "normal_user"

        vs = ViewSet(django_request, None)
        vs.perform_authentication(vs.request)

        assert vs.request.katka_auth_type == AuthType.GROUPS
        assert vs.request.katka_user_identifier == "normal_user"

    @override_settings(SCOPE_FULL_ACCESS="katka")
    def test_scopes(self, django_request):
        vs = ViewSet(django_request, ("katka",))
        vs.perform_authentication(vs.request)

        assert vs.request.katka_auth_type == AuthType.SCOPES
        assert vs.request.katka_user_identifier == "system_user"


class TestQuerySet:
    def test_anonymous(self, django_request):
        django_request.katka_auth_type = AuthType.ANONYMOUS

        vs = ViewSet(django_request, None)
        vs.get_user_restricted_queryset = mock.Mock(return_value=[])
        qs = vs.get_queryset()

        vs.get_user_restricted_queryset.assert_called_once()
        assert qs == []

    def test_normal_user(self, django_request):
        django_request.katka_auth_type = AuthType.GROUPS

        django_request.user.is_authenticated = True
        django_request.user.is_anonymous = False
        django_request.user.username = "normal_user"

        vs = ViewSet(django_request, None)
        vs.get_user_restricted_queryset = mock.Mock(return_value=[])
        qs = vs.get_queryset()

        vs.get_user_restricted_queryset.assert_called_once()
        assert qs == []

    @override_settings(SCOPE_FULL_ACCESS="katka")
    def test_missing_scopes(self, django_request):
        django_request.katka_auth_type = AuthType.SCOPES

        vs = ViewSet(django_request, ())
        vs.get_user_restricted_queryset = mock.Mock(return_value=[])
        with pytest.raises(PermissionDenied):
            vs.get_queryset()

        vs.perform_authentication(vs.request)

        vs.get_user_restricted_queryset.assert_not_called()

    @override_settings(SCOPE_FULL_ACCESS="katka")
    def test_correct_scope(self, django_request):
        django_request.katka_auth_type = AuthType.SCOPES
        django_request.user.is_authenticated = True

        vs = ViewSet(django_request, ("katka",))
        vs.get_user_restricted_queryset = mock.Mock(return_value=[])
        vs.perform_authentication(vs.request)
        qs = vs.get_queryset()

        vs.get_user_restricted_queryset.assert_not_called()
        assert qs is not None  # do not want to actually call the database by inspecting the queryset
