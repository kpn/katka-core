from django.contrib import admin

from katka.fields import username_on_model
from katka.models import Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    fields = ('name', 'group')

    def save_model(self, request, obj, form, change):
        with username_on_model(self.model, request.user.username):
            super().save_model(request, obj, form, change)
