from katka.constants import STATUS_ACTIVE
from katka.models import Credential, Team
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.relations import PrimaryKeyRelatedField


class GroupNameField(serializers.RelatedField):
    def to_internal_value(self, group_name):
        qs = self.get_queryset()
        try:
            return qs.get(name=group_name)
        except qs.model.DoesNotExist:
            raise NotFound

    def to_representation(self, group):
        return group.name


class PrimaryKeyRelated403Field(PrimaryKeyRelatedField):
    """
    Instead of replying with a 400 with a message 'does_not_exist', we would rather tell the user that they
    do not have permission because the referred team/credential/etc. either does not exist or they are not
    a member of a group that is linked to that object.
    """
    def fail(self, key, **kwargs):
        if key == 'does_not_exist':
            raise PermissionDenied(self.does_not_exist_message)

        return super().fail(key, **kwargs)


class TeamRelatedField(PrimaryKeyRelated403Field):
    does_not_exist_message = 'Team does not exist or you are not a member of its group'

    def get_queryset(self):
        """Only get the teams that are connected to a group that the user is a member of"""
        return Team.objects.filter(
            group__in=self.context['request'].user.groups.all(),
            status=STATUS_ACTIVE
        )


class CredentialRelatedField(PrimaryKeyRelated403Field):
    does_not_exist_message = 'Credential or team does not exist or is not linked to your group'

    def get_queryset(self):
        return Credential.objects.filter(
            team__group__in=self.context['request'].user.groups.all(),
            team__status=STATUS_ACTIVE,
            status=STATUS_ACTIVE,
        )
