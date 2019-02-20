from django.contrib import admin

from katka.fields import username_on_model
from katka.models import (
    Application, Credential, CredentialSecret, Project, SCMPipelineRun, SCMRepository, SCMService, SCMStepRun, Team,
)


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


@admin.register(Application)
class ApplicationAdmin(WithUsernameAdminModel):
    fields = ('name', 'slug', 'project')


@admin.register(Credential)
class CredentialAdmin(WithUsernameAdminModel):
    fields = ('name', 'slug', 'credential_type', 'team')


@admin.register(CredentialSecret)
class CredentialSecretAdmin(WithUsernameAdminModel):
    fields = ('key', 'value', 'credential')


@admin.register(SCMService)
class SCMServiceAdmin(WithUsernameAdminModel):
    fields = ('type', 'server_url')


@admin.register(SCMRepository)
class SCMRepositoryAdmin(WithUsernameAdminModel):
    fields = ('organisation', 'repository_name', 'credential', 'scm_service')


@admin.register(SCMPipelineRun)
class SCMPipelineRunAdmin(WithUsernameAdminModel):
    fields = ('commit_hash', 'status', 'steps_total', 'steps_completed', 'pipeline_yaml', 'application')


@admin.register(SCMStepRun)
class SCMStepRunAdmin(WithUsernameAdminModel):
    fields = ('slug', 'name', 'stage', 'status', 'output', 'scm_pipeline_run')
