from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group, User
from django.test.client import RequestFactory

import pytest
from katka.admin import CredentialAdmin, CredentialSecretAdmin, ProjectAdmin, TeamAdmin
from katka.fields import username_on_model
from katka.models import Credential, CredentialSecret, Project, Team


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


@pytest.fixture
def team(group):
    t = Team(name='team', group=group)
    with username_on_model(Team, 'audit_user'):
        t.save()
    return t


@pytest.fixture
def credential(team):
    c = Credential(name='team', team=team)
    with username_on_model(Credential, 'audit_user'):
        c.save()
    return c


@pytest.mark.django_db
class TestTeamAdmin:
    def test_save_stores_username(self, mock_request, group):
        t = TeamAdmin(Team, AdminSite())
        obj = Team(group=group)
        t.save_model(mock_request, obj, None, None)
        assert obj.created_username == 'mock1'
        assert obj.modified_username == 'mock1'


@pytest.mark.django_db
class TestProjectAdmin:
    def test_save_stores_username(self, mock_request, team):
        p = ProjectAdmin(Project, AdminSite())
        obj = Project(name='Project D', slug='PRJD', team=team)
        p.save_model(mock_request, obj, None, None)

        assert obj.created_username == 'mock1'
        assert obj.modified_username == 'mock1'


@pytest.mark.django_db
class TestCredentialAdmin:
    def test_save_stores_username(self, mock_request, team):
        c = CredentialAdmin(Credential, AdminSite())
        obj = Credential(name='Credential D', slug='CRED', team=team)
        c.save_model(mock_request, obj, None, None)

        assert obj.created_username == 'mock1'
        assert obj.modified_username == 'mock1'


@pytest.mark.django_db
class TestCredentialSecretAdmin:
    def test_save_stores_username(self, mock_request, credential):
        c = CredentialSecretAdmin(CredentialSecret, AdminSite())
        obj = CredentialSecret(key='access_key', value='supersecret', credential=credential)
        c.save_model(mock_request, obj, None, None)

        assert obj.created_username == 'mock1'
        assert obj.modified_username == 'mock1'
