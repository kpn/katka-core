from django.contrib import admin

from katka.fields import username_on_model
from katka.models import Credential, CredentialSecret, Project, Team


class WithUsernameAdminModel(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        with username_on_model(self.model, request.user.username):
            super().save_model(request, obj, form, change)


@admin.register(Team)
class TeamAdmin(WithUsernameAdminModel):
    fields = ('name', 'group')


@admin.register(Project)
class ProjectAdmin(WithUsernameAdminModel):
    fields = ('name', 'slug', 'team')


@admin.register(Credential)
class CredentialAdmin(WithUsernameAdminModel):
    fields = ('name', 'slug', 'credential_type', 'team')


@admin.register(CredentialSecret)
class CredentialSecretAdmin(WithUsernameAdminModel):
    fields = ('key', 'value', 'credential')
