from django.contrib import admin
from django.urls import include, path

from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from . import views

app_name = 'katka_core'

router = routers.SimpleRouter()
router.register('team', views.TeamViewSet, basename='team')
router.register('project', views.ProjectViewSet, basename='project')

project_router = NestedSimpleRouter(router, 'team', lookup='team')
project_router.register('project', views.ProjectViewSet, basename='project')

credential_router = NestedSimpleRouter(router, 'team', lookup='team')
credential_router.register('credential', views.CredentialViewSet, basename='credential')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('', include(project_router.urls)),
    path('', include(credential_router.urls)),
]
