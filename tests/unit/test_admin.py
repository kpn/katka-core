from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group, User
from django.test.client import RequestFactory

import pytest
from katka.admin import (
    ApplicationAdmin, CredentialAdmin, CredentialSecretAdmin, ProjectAdmin, SCMPipelineRunAdmin, SCMRepositoryAdmin,
    SCMServiceAdmin, SCMStepRunAdmin, TeamAdmin,
)
from katka.fields import username_on_model
from katka.models import (
    Application, Credential, CredentialSecret, Project, SCMPipelineRun, SCMRepository, SCMService, SCMStepRun, Team,
)


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
def project(team):
    p = Project(name='project1', team=team)
    with username_on_model(Project, 'audit_user'):
        p.save()
    return p


@pytest.fixture
def credential(team):
    c = Credential(name='credential1', team=team)
    with username_on_model(Credential, 'audit_user'):
        c.save()
    return c


@pytest.fixture
def scm_service():
    scm_service = SCMService(scm_service_type='bitbucket', server_url='www.example.com')
    with username_on_model(SCMService, 'audit_user'):
        scm_service.save()
    return scm_service


@pytest.fixture
def scm_repository(scm_service, credential):
    scm_repository = SCMRepository(scm_service=scm_service, credential=credential,
                                   organisation='acme', repository_name='sample')
    with username_on_model(SCMRepository, 'audit_user'):
        scm_repository.save()
    return scm_repository


@pytest.fixture
def application(project, scm_repository):
    app = Application(name='application1', project=project, scm_repository=scm_repository)
    with username_on_model(Application, 'audit_user'):
        app.save()
    return app


@pytest.fixture
def scm_pipeline_run(application):
    pipeline_yaml = '''stages:
      - release

    do-release:
      stage: release
    '''
    scm_pipeline_run = SCMPipelineRun(application=application,
                                      pipeline_yaml=pipeline_yaml,
                                      status='in progress',
                                      steps_total=5,
                                      commit_hash='4015B57A143AEC5156FD1444A017A32137A3FD0F')
    with username_on_model(SCMPipelineRun, 'audit_user'):
        scm_pipeline_run.save()

    return scm_pipeline_run


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
class TestApplicationAdmin:
    def test_save_stores_username(self, mock_request, project, scm_repository):
        a = ApplicationAdmin(Application, AdminSite())
        obj = Application(name='Application D', slug='APPD', project=project, scm_repository=scm_repository)
        a.save_model(mock_request, obj, None, None)

        assert obj.created_username == 'mock1'
        assert obj.modified_username == 'mock1'


@pytest.mark.django_db
class TestCredentialAdmin:
    def test_save_stores_username(self, mock_request, team):
        c = CredentialAdmin(Credential, AdminSite())
        obj = Credential(name='Credential D', team=team)
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


@pytest.mark.django_db
class TestSCMServiceAdmin:
    def test_save_stores_username(self, mock_request):
        c = SCMServiceAdmin(SCMService, AdminSite())
        obj = SCMService(scm_service_type='git', server_url='www.example.com')
        c.save_model(mock_request, obj, None, None)

        assert obj.created_username == 'mock1'
        assert obj.modified_username == 'mock1'


@pytest.mark.django_db
class TestSCMRepositoryAdmin:
    def test_save_stores_username(self, mock_request, credential, scm_service):
        c = SCMRepositoryAdmin(SCMRepository, AdminSite())
        obj = SCMRepository(organisation='mock', repository_name='katka',
                            credential=credential, scm_service=scm_service)
        c.save_model(mock_request, obj, None, None)

        assert obj.created_username == 'mock1'
        assert obj.modified_username == 'mock1'


@pytest.mark.django_db
class TestSCMPipelineRunAdmin:
    def test_save_stores_username(self, mock_request, application):
        c = SCMPipelineRunAdmin(SCMPipelineRun, AdminSite())
        obj = SCMPipelineRun(commit_hash='4015B57A143AEC5156FD1444A017A32137A3FD0F',
                             status='in progress',
                             steps_total=5,
                             application=application)
        c.save_model(mock_request, obj, None, None)

        assert obj.created_username == 'mock1'
        assert obj.modified_username == 'mock1'


@pytest.mark.django_db
class TestSCMStepRunAdmin:
    def test_save_stores_username(self, mock_request, scm_pipeline_run):
        c = SCMStepRunAdmin(SCMStepRun, AdminSite())
        obj = SCMStepRun(slug='release', name='Release Katka', stage='Production',
                         status='in progress',
                         scm_pipeline_run=scm_pipeline_run)
        c.save_model(mock_request, obj, None, None)

        assert obj.created_username == 'mock1'
        assert obj.modified_username == 'mock1'
