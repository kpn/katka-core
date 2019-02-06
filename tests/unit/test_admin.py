from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group, User
from django.test.client import RequestFactory

import pytest
from katka.admin import TeamAdmin
from katka.models import Team


@pytest.fixture
def mock_request():
    factory = RequestFactory()
    request = factory.get('/')
    request.user = User(username='mock1')
    return request


@pytest.fixture
def group():
    g = Group(name='group1')
    g.save()
    return g


@pytest.mark.django_db
class TestTeamAdmin:
    def test_save_stores_username(self, mock_request, group):
        t = TeamAdmin(Team, AdminSite())
        obj = Team(group=group)
        t.save_model(mock_request, obj, None, None)
        assert obj.created_username == 'mock1'
        assert obj.modified_username == 'mock1'
