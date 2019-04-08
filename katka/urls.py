from django.contrib import admin
from django.urls import include, path

from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from . import views

app_name = 'katka_core'

router = routers.SimpleRouter()
router.register('teams', views.TeamViewSet, basename='teams')
router.register('projects', views.ProjectViewSet, basename='projects')
router.register('applications', views.ApplicationViewSet, basename='applications')
router.register('credentials', views.CredentialViewSet, basename='credentials')
router.register('scm-services', views.SCMServiceViewSet, basename='scm-services')
router.register('scm-repositories', views.SCMRepositoryViewSet, basename='scm-repositories')
router.register('scm-pipeline-runs', views.SCMPipelineRunViewSet, basename='scm-pipeline-runs')
router.register('scm-step-runs', views.SCMStepRunViewSet, basename='scm-step-runs')
router.register('scm-releases', views.SCMReleaseViewSet, basename='scm-releases')


secrets_router = NestedSimpleRouter(router, 'credentials', lookup='credentials')
secrets_router.register('secrets', views.CredentialSecretsViewSet, basename='secrets')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('', include(secrets_router.urls)),
]
