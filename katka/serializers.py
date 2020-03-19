from django.contrib.auth.models import Group

from katka.auth import has_full_access_scope
from katka.constants import STEP_STATUS_CHOICES
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
from katka.serializer_fields import (
    ApplicationRelatedField,
    CredentialRelatedField,
    GroupNameField,
    ProjectRelatedField,
    SCMPipelineRunRelatedField,
    SCMRepositoryRelatedField,
    SCMServiceRelatedField,
    TeamRelatedField,
)
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied


class KatkaSerializer(serializers.ModelSerializer):
    pass


class TeamSerializer(KatkaSerializer):
    group = GroupNameField(queryset=Group.objects.all())

    class Meta:
        model = Team
        fields = ("public_identifier", "slug", "name", "group")

    def validate_group(self, group):
        if has_full_access_scope(self.context["request"]):
            querystring = Group.objects
        else:
            querystring = self.context["request"].user.groups

        querystring = querystring.filter(name=group.name)
        if not querystring.exists():
            raise PermissionDenied("Group does not exist or user is not a member of this group")

        return group


class ProjectSerializer(KatkaSerializer):
    team = TeamRelatedField()

    class Meta:
        model = Project
        fields = ("public_identifier", "slug", "name", "team")


class ApplicationSerializer(KatkaSerializer):
    project = ProjectRelatedField()
    scm_repository = SCMRepositoryRelatedField()

    class Meta:
        model = Application
        fields = ("public_identifier", "slug", "name", "project", "scm_repository", "active")


class CredentialSerializer(KatkaSerializer):
    team = TeamRelatedField()

    class Meta:
        model = Credential
        fields = ("public_identifier", "name", "team")


class CredentialSecretSerializer(serializers.ModelSerializer):
    credential = CredentialRelatedField()

    class Meta:
        model = CredentialSecret
        fields = ("key", "value", "credential")

    def to_internal_value(self, data):
        """Automatically add credential pk based on url kwargs"""
        data["credential"] = self.context["view"].kwargs["credentials_pk"]
        return super().to_internal_value(data)


class SCMServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SCMService
        fields = ("public_identifier", "scm_service_type", "server_url")


class SCMRepositorySerializer(KatkaSerializer):
    credential = CredentialRelatedField()
    scm_service = SCMServiceRelatedField()

    class Meta:
        model = SCMRepository
        fields = ("public_identifier", "organisation", "repository_name", "credential", "scm_service")


class SCMPipelineRunSerializer(KatkaSerializer):
    application = ApplicationRelatedField()

    class Meta:
        model = SCMPipelineRun
        fields = (
            "public_identifier",
            "commit_hash",
            "first_parent_hash",
            "status",
            "steps_total",
            "steps_completed",
            "pipeline_yaml",
            "application",
            "scmrelease_set",
            "output",
        )
        read_only_fields = ("scmrelease_set",)


class SCMStepRunSerializer(KatkaSerializer):
    scm_pipeline_run = SCMPipelineRunRelatedField()

    class Meta:
        model = SCMStepRun
        fields = (
            "public_identifier",
            "step_type",
            "slug",
            "name",
            "stage",
            "status",
            "output",
            "sequence_id",
            "scm_pipeline_run",
            "tags",
            "started_at",
            "ended_at",
        )


class SCMStepRunUpdateSerializer(KatkaSerializer):
    # it seems redundant to declare this field here as it is declared in the model, but in this
    # context it's a required field and in the model it's optional, thus the duplication.
    status = serializers.ChoiceField(required=True, choices=STEP_STATUS_CHOICES)

    class Meta:
        model = SCMStepRun
        fields = ("public_identifier", "status", "ended_at")

    def __init__(self, *args, **kwargs):
        kwargs["partial"] = False  # otherwise DRF will allow empty status
        super().__init__(*args, **kwargs)


class SCMReleaseSerializer(KatkaSerializer):
    scm_pipeline_runs = SCMPipelineRunRelatedField(required=False, read_only=True, many=True)

    class Meta:
        model = SCMRelease
        fields = ("public_identifier", "name", "started_at", "ended_at", "scm_pipeline_runs", "status")
        read_only_fields = ("started_at", "ended_at", "scm_pipeline_runs")


class SCMReleaseCreateSerializer(KatkaSerializer):
    scm_pipeline_runs = SCMPipelineRunRelatedField(required=False, many=True)

    class Meta:
        model = SCMRelease
        fields = ("name", "scm_pipeline_runs", "status")


class ApplicationMetadataSerializer(serializers.ModelSerializer):
    application = ApplicationRelatedField()

    class Meta:
        model = ApplicationMetadata
        fields = ("key", "value", "application")

    def to_internal_value(self, data):
        """Automatically add application pk based on url kwargs"""
        data["application"] = self.context["view"].kwargs["applications_pk"]
        return super().to_internal_value(data)
