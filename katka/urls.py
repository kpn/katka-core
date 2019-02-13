from django.contrib import admin
from django.urls import include, path

from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from . import views

app_name = 'katka_core'

router = routers.SimpleRouter()
router.register('teams', views.TeamViewSet, basename='teams')
router.register('projects', views.ProjectViewSet, basename='projects')
router.register('credentials', views.CredentialViewSet, basename='credentials')

secrets_router = NestedSimpleRouter(router, 'credentials', lookup='credentials')
secrets_router.register('secrets', views.CredentialSecretsViewSet, basename='secrets')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('', include(secrets_router.urls)),
]
