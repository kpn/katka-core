from django.contrib import admin

from katka.fields import username_on_model
from katka.models import (
    Application,
    ApplicationMetadata,
    Credential,
    CredentialSecret,
    Project,
    SCMPipelineRun,
    SCMRelease,
    SCMRepository,
    SCMService,
    SCMStepRun,
    Team,
)


class ReadOnlyAuditFieldsMixin:
    readonly_fields = ("created_at", "created_username", "modified_at", "modified_username", "deleted")


class WithUsernameAdminModel(admin.ModelAdmin, ReadOnlyAuditFieldsMixin):
    def save_model(self, request, obj, form, change):
        with username_on_model(self.model, request.user.username):
            super().save_model(request, obj, form, change)


@admin.register(Team)
class TeamAdmin(WithUsernameAdminModel):
    fields = ("name", "slug", "group")


@admin.register(Project)
class ProjectAdmin(WithUsernameAdminModel):
    fields = ("name", "slug", "team")


@admin.register(Application)
class ApplicationAdmin(WithUsernameAdminModel):
    fields = ("name", "slug", "project", "scm_repository")


@admin.register(Credential)
class CredentialAdmin(WithUsernameAdminModel):
    fields = ("name", "credential_type", "team")


@admin.register(CredentialSecret)
class CredentialSecretAdmin(WithUsernameAdminModel):
    fields = ("key", "value", "credential")


@admin.register(SCMService)
class SCMServiceAdmin(WithUsernameAdminModel):
    fields = ("scm_service_type", "server_url")


@admin.register(SCMRepository)
class SCMRepositoryAdmin(WithUsernameAdminModel):
    fields = ("organisation", "repository_name", "credential", "scm_service")
    list_display = ("pk", "scm_service", "organisation", "repository_name")


@admin.register(SCMPipelineRun)
class SCMPipelineRunAdmin(WithUsernameAdminModel):
    fields = (
        "commit_hash",
        "first_parent_hash",
        "status",
        "steps_total",
        "steps_completed",
        "pipeline_yaml",
        "application",
    )
    list_display = ("pk", "application", "commit_hash", "first_parent_hash", "created_at")
    list_filter = ("application__name",)
    ordering = ("created_at",)


@admin.register(SCMStepRun)
class SCMStepRunAdmin(WithUsernameAdminModel):
    fields = ("slug", "name", "stage", "status", "output", "started_at", "ended_at", "scm_pipeline_run")
    list_display = ("pk", "scm_pipeline_run", "name", "stage", "status", "created_at", "started_at", "ended_at")
    list_filter = ("scm_pipeline_run__application__name",)
    ordering = ("created_at",)


@admin.register(ApplicationMetadata)
class ApplicationMetadataAdmin(WithUsernameAdminModel):
    fields = ("key", "value", "application")
    list_display = ("pk", "application", "key")


@admin.register(SCMRelease)
class SCMReleaseAdmin(WithUsernameAdminModel):
    fields = ("name", "status", "started_at", "ended_at", "scm_pipeline_runs")
    list_display = ("pk", "name", "status", "created_at", "started_at", "ended_at")
    ordering = ("created_at",)
