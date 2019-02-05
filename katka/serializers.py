from django.contrib.auth.models import Group

from katka.models import Team
from rest_framework import serializers


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('public_identifier', 'name', 'group')

    def to_internal_value(self, data):
        group_name = data.pop('group', None)
        if group_name is not None:
            data['group'] = Group.objects.get(name=group_name).pk

        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['group'] = instance.group.name
        return data
