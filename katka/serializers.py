from django.contrib.auth.models import Group

from katka.models import Team
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
        fields = ('public_identifier', 'name', 'group')

    def validate_group(self, group):
        if not self.context['request'].user.groups.filter(name=group.name).exists():
            raise PermissionDenied('User is not a member of this group')

        return group
