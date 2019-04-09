from katka.models import (
    Application, Credential, CredentialSecret, Project, SCMPipelineRun, SCMRelease, SCMRepository, SCMService,
    SCMStepRun, Team,
)
from katka.serializers import (
    ApplicationSerializer, CredentialSecretSerializer, CredentialSerializer, ProjectSerializer,
    SCMPipelineRunSerializer, SCMReleaseCreateSerializer, SCMReleaseSerializer, SCMRepositorySerializer,
    SCMServiceSerializer, SCMStepRunSerializer, TeamSerializer,
)
from katka.viewsets import AuditViewSet, FilterViewMixin, ReadOnlyAuditViewMixin
from rest_framework.permissions import IsAuthenticated


class TeamViewSet(FilterViewMixin, AuditViewSet):
    model = Team
    serializer_class = TeamSerializer
    lookup_field = 'public_identifier'
    lookup_value_regex = '[0-9a-f-]{36}'

    def get_queryset(self):
        # Only show teams that are linked to a group that the user is part of
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(group__in=user_groups)


class ProjectViewSet(FilterViewMixin, AuditViewSet):
    model = Project
    serializer_class = ProjectSerializer

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(team__group__in=user_groups)


class ApplicationViewSet(FilterViewMixin, AuditViewSet):
    model = Application
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(project__team__group__in=user_groups)


class CredentialViewSet(FilterViewMixin, AuditViewSet):
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
        kwargs = {
            'credential__team__group__in': user_groups,
            'credential__deleted': False,
            'credential': self.kwargs['credentials_pk'],
        }
        return super().get_queryset().filter(**kwargs)


class SCMServiceViewSet(ReadOnlyAuditViewMixin):
    model = SCMService
    serializer_class = SCMServiceSerializer
    permission_classes = [IsAuthenticated]


class SCMRepositoryViewSet(FilterViewMixin, AuditViewSet):
    model = SCMRepository
    serializer_class = SCMRepositorySerializer

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(credential__team__group__in=user_groups)


class SCMPipelineRunViewSet(FilterViewMixin, AuditViewSet):
    model = SCMPipelineRun
    serializer_class = SCMPipelineRunSerializer

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(application__project__team__group__in=user_groups)


class SCMStepRunViewSet(FilterViewMixin, AuditViewSet):
    model = SCMStepRun
    serializer_class = SCMStepRunSerializer

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(scm_pipeline_run__application__project__team__group__in=user_groups)


class SCMReleaseViewSet(FilterViewMixin, AuditViewSet):
    model = SCMRelease
    serializer_class = SCMReleaseSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SCMReleaseCreateSerializer

        return self.serializer_class

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(scm_pipeline_run__application__project__team__group__in=user_groups)
