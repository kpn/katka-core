from unittest import mock

from django.http import HttpRequest
from django.test import override_settings

import pytest
from rest_framework.exceptions import PermissionDenied
from tests.unit.viewsets import ViewSet


@pytest.fixture
def django_request():
    req = HttpRequest()
    req.method = "OPTIONS"
    req.user = mock.Mock()
    req.user.is_authenticated = False
    req.user.is_anonymous = True
    return req


class TestUserOrScopeViewSet:
    def test_anonymous(self, django_request):
        vs = ViewSet(django_request, None)
        vs.get_user_restricted_queryset = mock.Mock(return_value=[])
        qs = vs.get_queryset()

        vs.get_user_restricted_queryset.assert_called_once()
        assert qs == []

        assert django_request.katka_user_identifier == "anonymous"

    def test_normal_user(self, django_request):
        django_request.user.is_authenticated = True
        django_request.user.is_anonymous = False
        django_request.user.username = "normal_user"
        vs = ViewSet(django_request, None)
        vs.get_user_restricted_queryset = mock.Mock(return_value=[])
        qs = vs.get_queryset()

        vs.get_user_restricted_queryset.assert_called_once()
        assert qs == []

        assert django_request.katka_user_identifier == "normal_user"

    @override_settings(SCOPE_FULL_ACCESS="katka")
    def test_missing_scopes(self, django_request):
        vs = ViewSet(django_request, ())
        vs.get_user_restricted_queryset = mock.Mock(return_value=[])
        with pytest.raises(PermissionDenied):
            vs.get_queryset()

        vs.get_user_restricted_queryset.assert_not_called()

        assert django_request.katka_user_identifier == "system_user"

    @override_settings(SCOPE_FULL_ACCESS="katka")
    def test_correct_scope(self, django_request):
        django_request.user.is_authenticated = True
        vs = ViewSet(django_request, ("katka",))
        vs.get_user_restricted_queryset = mock.Mock(return_value=[])
        qs = vs.get_queryset()

        vs.get_user_restricted_queryset.assert_not_called()
        assert qs is not None  # do not want to actually call the database by inspecting the queryset

        assert django_request.katka_user_identifier == "system_user"
