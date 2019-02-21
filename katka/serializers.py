from django.contrib.auth.models import Group

from katka.models import (
    Application, Credential, CredentialSecret, Project, SCMPipelineRun, SCMRepository, SCMService, SCMStepRun, Team,
)
from katka.serializer_fields import (
    ApplicationRelatedField, CredentialRelatedField, GroupNameField, ProjectRelatedField, SCMPipelineRunRelatedField,
    SCMRepositoryRelatedField, SCMServiceRelatedField, TeamRelatedField,
)
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied


class TeamSerializer(serializers.ModelSerializer):
    group = GroupNameField(queryset=Group.objects.all())

    class Meta:
        model = Team
        fields = ('public_identifier', 'slug', 'name', 'group')

    def validate_group(self, group):
        if not self.context['request'].user.groups.filter(name=group.name).exists():
            raise PermissionDenied('User is not a member of this group')

        return group


class ProjectSerializer(serializers.ModelSerializer):
    team = TeamRelatedField()

    class Meta:
        model = Project
        fields = ('public_identifier', 'slug', 'name', 'team')


class ApplicationSerializer(serializers.ModelSerializer):
    project = ProjectRelatedField()
    scm_repository = SCMRepositoryRelatedField()

    class Meta:
        model = Application
        fields = ('public_identifier', 'slug', 'name', 'project', 'scm_repository')


class CredentialSerializer(serializers.ModelSerializer):
    team = TeamRelatedField()

    class Meta:
        model = Credential
        fields = ('public_identifier', 'name', 'slug', 'team')


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
        fields = ('public_identifier', 'type', 'server_url')


class SCMRepositorySerializer(serializers.ModelSerializer):
    credential = CredentialRelatedField()
    scm_service = SCMServiceRelatedField()

    class Meta:
        model = SCMRepository
        fields = ('public_identifier', 'organisation', 'repository_name', 'credential', 'scm_service')


class SCMPipelineRunSerializer(serializers.ModelSerializer):
    application = ApplicationRelatedField()

    class Meta:
        model = SCMPipelineRun
        fields = ('public_identifier', 'commit_hash', 'status', 'steps_total', 'steps_completed', 'pipeline_yaml',
                  'application')


class SCMStepRunSerializer(serializers.ModelSerializer):
    scm_pipeline_run = SCMPipelineRunRelatedField()

    class Meta:
        model = SCMStepRun
        fields = ('public_identifier', 'slug', 'name', 'stage', 'status', 'output', 'scm_pipeline_run')
