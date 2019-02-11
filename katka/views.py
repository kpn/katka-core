from katka.models import Credential, Project, Team
from katka.serializers import CredentialSerializer, ProjectSerializer, TeamSerializer
from katka.viewsets import AuditViewSet


class TeamViewSet(AuditViewSet):
    model = Team
    serializer_class = TeamSerializer
    lookup_field = 'public_identifier'
    lookup_value_regex = '[0-9a-f-]{36}'

    def get_queryset(self):
        # Only show teams that are linked to a group that the user is part of
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(group__in=user_groups)


class ProjectViewSet(AuditViewSet):
    model = Project
    serializer_class = ProjectSerializer

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(team__group__in=user_groups)


class CredentialViewSet(AuditViewSet):
    model = Credential
    serializer_class = CredentialSerializer

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(team__group__in=user_groups)
