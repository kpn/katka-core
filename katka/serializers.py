from django.contrib.auth.models import Group

from katka.models import Credential, Project, Team
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied


class GroupNameField(serializers.RelatedField):
    def to_internal_value(self, group_name):
        qs = self.get_queryset()
        try:
            return qs.get(name=group_name)
        except qs.model.DoesNotExist:
            raise NotFound

    def to_representation(self, group):
        return group.name


class TeamSerializer(serializers.ModelSerializer):
    group = GroupNameField(queryset=Group.objects.all())

    class Meta:
        model = Team
        fields = ('public_identifier', 'slug', 'name', 'group')

    def validate_group(self, group):
        if not self.context['request'].user.groups.filter(name=group.name).exists():
            raise PermissionDenied('User is not a member of this group')

        return group


class EmbeddedTeamSerializer(serializers.Serializer):
    """
    Instead of using a serializers.PrimaryKeyRelatedField to show only the public_identifier,
    this serializer shows both pi and slug. Both slug and pi can be used in the URL to access
    objects.
    """
    public_identifier = serializers.UUIDField(required=False)
    slug = serializers.SlugField(required=False)


class TeamChildMixin:
    def to_internal_value(self, data):
        # Can't put this on the EmbeddedTeamSerializer because it will never be called (team is not required and
        # read-only, so it's not allowed to pass the team when modifying something).
        data = super().to_internal_value(data)
        try:
            data['team'] = Team.objects.get(public_identifier=self.context['view'].kwargs['team_public_identifier'])
        except Team.DoesNotExist:
            raise NotFound

        return data

    def validate(self, attrs):
        # since 'team' is not required and read-only, it will not be present on a create/update
        # therefore, validate_team() will not be called, but validate() will. Because to_internal_value() will
        # add a 'team', we can validate it here.

        if not self.context['request'].user.groups.filter(name=attrs['team'].group.name).exists():
            raise PermissionDenied('User is not a member of this group')

        return super().validate(attrs)


class ProjectSerializer(TeamChildMixin, serializers.ModelSerializer):
    team = EmbeddedTeamSerializer(required=False, read_only=True)

    class Meta:
        model = Project
        fields = ('public_identifier', 'slug', 'name', 'team')


class CredentialSerializer(TeamChildMixin, serializers.ModelSerializer):
    team = EmbeddedTeamSerializer(required=False, read_only=True)

    class Meta:
        model = Credential
        fields = ('name', 'slug', 'team')
