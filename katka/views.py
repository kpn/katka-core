from katka.models import (
    Application, Credential, CredentialSecret, Project, SCMPipelineRun, SCMRepository, SCMService, SCMStepRun, Team,
)
from katka.serializers import (
    ApplicationSerializer, CredentialSecretSerializer, CredentialSerializer, ProjectSerializer,
    SCMPipelineRunSerializer, SCMRepositorySerializer, SCMServiceSerializer, SCMStepRunSerializer, TeamSerializer,
)
from katka.viewsets import AuditViewSet, ReadOnlyAuditViewMixin
from rest_framework.permissions import IsAuthenticated


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


class ApplicationViewSet(AuditViewSet):
    model = Application
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(project__team__group__in=user_groups)


class CredentialViewSet(AuditViewSet):
    model = Credential
    serializer_class = CredentialSerializer

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(team__group__in=user_groups)


class CredentialSecretsViewSet(AuditViewSet):
    model = CredentialSecret
    serializer_class = CredentialSecretSerializer
    lookup_field = 'key'

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(credential__team__group__in=user_groups)


class SCMServiceViewSet(ReadOnlyAuditViewMixin):
    model = SCMService
    serializer_class = SCMServiceSerializer
    permission_classes = [IsAuthenticated]


class SCMRepositoryViewSet(AuditViewSet):
    model = SCMRepository
    serializer_class = SCMRepositorySerializer

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(credential__team__group__in=user_groups)


class SCMPipelineRunViewSet(AuditViewSet):
    model = SCMPipelineRun
    serializer_class = SCMPipelineRunSerializer

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(application__project__team__group__in=user_groups)


class SCMStepRunViewSet(AuditViewSet):
    model = SCMStepRun
    serializer_class = SCMStepRunSerializer

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(scm_pipeline_run__application__project__team__group__in=user_groups)
