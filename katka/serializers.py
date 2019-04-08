from django.contrib.auth.models import Group

from katka.models import (
    Application, Credential, CredentialSecret, Project, SCMPipelineRun, SCMRelease, SCMRepository, SCMService,
    SCMStepRun, Team,
)
from katka.serializer_fields import (
    ApplicationRelatedField, CredentialRelatedField, GroupNameField, ProjectRelatedField, SCMPipelineRunRelatedField,
    SCMRepositoryRelatedField, SCMServiceRelatedField, TeamRelatedField,
)
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied


class KatkaSerializer(serializers.ModelSerializer):
    @classmethod
    def get_related_fields(cls):
        """
        Gets the fields that are declared in the Class declaration
        These are the related fields (e.g. project for an application)
        """
        return cls._get_declared_fields([cls], {})


class TeamSerializer(KatkaSerializer):
    group = GroupNameField(queryset=Group.objects.all())

    class Meta:
        model = Team
        fields = ('public_identifier', 'slug', 'name', 'group')

    def validate_group(self, group):
        if not self.context['request'].user.groups.filter(name=group.name).exists():
            raise PermissionDenied('User is not a member of this group')

        return group


class ProjectSerializer(KatkaSerializer):
    team = TeamRelatedField()

    class Meta:
        model = Project
        fields = ('public_identifier', 'slug', 'name', 'team')


class ApplicationSerializer(KatkaSerializer):
    project = ProjectRelatedField()
    scm_repository = SCMRepositoryRelatedField()

    class Meta:
        model = Application
        fields = ('public_identifier', 'slug', 'name', 'project', 'scm_repository')


class CredentialSerializer(KatkaSerializer):
    team = TeamRelatedField()

    class Meta:
        model = Credential
        fields = ('public_identifier', 'name', 'team')


class CredentialSecretSerializer(serializers.ModelSerializer):
    credential = CredentialRelatedField()

    class Meta:
        model = CredentialSecret
        fields = ('key', 'value', 'credential')

    def to_internal_value(self, data):
        """Automatically add credential pk based on url kwargs"""
        data['credential'] = self.context['view'].kwargs['credentials_pk']
        return super().to_internal_value(data)


class SCMServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = SCMService
        fields = ('public_identifier', 'scm_service_type', 'server_url')


class SCMRepositorySerializer(KatkaSerializer):
    credential = CredentialRelatedField()
    scm_service = SCMServiceRelatedField()

    class Meta:
        model = SCMRepository
        fields = ('public_identifier', 'organisation', 'repository_name', 'credential', 'scm_service')


class SCMPipelineRunSerializer(KatkaSerializer):
    application = ApplicationRelatedField()

    class Meta:
        model = SCMPipelineRun
        fields = ('public_identifier', 'commit_hash', 'status', 'steps_total', 'steps_completed', 'pipeline_yaml',
                  'application')


class SCMStepRunSerializer(KatkaSerializer):
    scm_pipeline_run = SCMPipelineRunRelatedField()

    class Meta:
        model = SCMStepRun
        fields = ('public_identifier', 'slug', 'name', 'stage', 'status', 'output', 'scm_pipeline_run')


class SCMReleaseSerializer(KatkaSerializer):
    scm_pipeline_run = SCMPipelineRunRelatedField(required=False, read_only=True)

    released = serializers.DateTimeField(required=False)

    class Meta:
        model = SCMRelease
        fields = ('public_identifier', 'name', 'released', 'from_hash', 'to_hash', 'scm_pipeline_run')
        read_only_fields = ('from_hash', 'to_hash', 'scm_pipeline_run')


class SCMReleaseCreateSerializer(KatkaSerializer):
    scm_pipeline_run = SCMPipelineRunRelatedField(required=False)

    released = serializers.DateTimeField(required=False)

    class Meta:
        model = SCMRelease
        fields = ('public_identifier', 'name', 'released', 'from_hash', 'to_hash', 'scm_pipeline_run')
