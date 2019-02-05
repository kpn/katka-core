from django.contrib import admin
from django.urls import include, path

from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register('team', views.TeamViewSet, basename='team')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
