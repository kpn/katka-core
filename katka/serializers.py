from django.contrib.auth.models import Group

from katka.models import Credential, CredentialSecret, Project, Team
from katka.serializer_fields import CredentialRelatedField, GroupNameField, TeamRelatedField
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


class CredentialSerializer(serializers.ModelSerializer):
    team = TeamRelatedField()

    class Meta:
        model = Credential
        fields = ('name', 'slug', 'team')


class CredentialSecretSerializer(serializers.ModelSerializer):
    credential = CredentialRelatedField()

    class Meta:
        model = CredentialSecret
        fields = ('key', 'value', 'credential')

    def to_internal_value(self, data):
        """Automatically add credential pk based on url kwargs"""
        data['credential'] = self.context['view'].kwargs['credentials_pk']
        return super().to_internal_value(data)
