import logging
from datetime import datetime

from django.conf import settings
from django.db import IntegrityError

import pytz
from katka.constants import (
    PIPELINE_FINAL_STATUSES,
    PIPELINE_STATUS_IN_PROGRESS,
    PIPELINE_STATUS_INITIALIZING,
    PIPELINE_STATUS_QUEUED,
    STEP_FINAL_STATUSES,
)
from katka.exceptions import AlreadyExists, ParentCommitMissing
from katka.models import (
    Application,
    ApplicationMetadata,
    Credential,
    CredentialSecret,
    Project,
    SCMPipelineRun,
    SCMRelease,
    SCMRepository,
    SCMService,
    SCMStepRun,
    Team,
)
from katka.serializers import (
    ApplicationMetadataSerializer,
    ApplicationSerializer,
    CredentialSecretSerializer,
    CredentialSerializer,
    ProjectSerializer,
    SCMPipelineRunSerializer,
    SCMReleaseSerializer,
    SCMRepositorySerializer,
    SCMServiceSerializer,
    SCMStepRunSerializer,
    SCMStepRunUpdateSerializer,
    TeamSerializer,
)
from katka.viewsets import AuditViewSet, FilterViewMixin, ReadOnlyAuditViewMixin, UpdateAuditMixin
from rest_framework.permissions import IsAuthenticated

log = logging.getLogger(__name__)


class TeamViewSet(FilterViewMixin, AuditViewSet):
    model = Team
    serializer_class = TeamSerializer
    lookup_field = "public_identifier"
    lookup_value_regex = "[0-9a-f-]{36}"
    parameter_lookup_map = {"application": "project__application"}

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
    lookup_field = "key"

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        kwargs = {
            "credential__team__group__in": user_groups,
            "credential__deleted": False,
            "credential": self.kwargs["credentials_pk"],
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

    parameter_lookup_map = {
        "scmrelease": "scmrelease",
        "release": "scmrelease",
    }

    def _can_create(self, application, parent_hash):
        if parent_hash is None:
            return True  # this is probably the first commit

        try:
            self.model.objects.get(application=application, commit_hash=parent_hash)
        except self.model.DoesNotExist:
            return False  # parent commit does not exist, we need a sync before we can continue

        return True

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            raise AlreadyExists()

    def perform_create(self, serializer):
        if not self._can_create(
            serializer.validated_data["application"], serializer.validated_data.get("first_parent_hash")
        ):
            raise ParentCommitMissing()
        super().perform_create(serializer)

    def _ready_to_run(self, pipeline_run):
        if pipeline_run.first_parent_hash is None:
            return True  # this is probably the first commit

        try:
            parent_instance = self.model.objects.get(
                application=pipeline_run.application, commit_hash=pipeline_run.first_parent_hash
            )
        except self.model.DoesNotExist:
            # parent commit does not exist, can't run. This should not happen since we are only creating pipeline runs
            # with a defined parent commit
            log.exception(
                f"Parent pipeline run with hash {pipeline_run.first_parent_hash} could not "
                f"be found for pipeline run {pipeline_run.public_identifier}. This should not be the case since "
                f"pipeline runs with no parent are not added to the DB (exception being the initial commit)."
            )
            return False

        if parent_instance.status not in PIPELINE_FINAL_STATUSES:
            return False  # exists, but not ready to run this one yet

        return True

    def perform_update(self, serializer):
        status = serializer.validated_data.get("status", None)
        if status == PIPELINE_STATUS_IN_PROGRESS:
            if not self._ready_to_run(serializer.instance):
                serializer.validated_data["status"] = PIPELINE_STATUS_QUEUED

        super().perform_update(serializer)

        if status in PIPELINE_FINAL_STATUSES:
            self._run_next_pipeline_if_available(serializer.instance.application, serializer.instance.commit_hash)

    def _run_next_pipeline_if_available(self, application, commit_hash):
        try:
            next_pipeline = self.model.objects.get(application=application, first_parent_hash=commit_hash)
        except self.model.DoesNotExist:
            return  # does not exist (yet), so nothing to do

        if next_pipeline.status != PIPELINE_STATUS_QUEUED:
            if next_pipeline.status != PIPELINE_STATUS_INITIALIZING:
                log.warning(
                    f'Next pipeline {next_pipeline.pk} is not queued, it has status "{next_pipeline.status}", '
                    "not updating"
                )
            return

        # No need to wrap inside a "with username_on_model():" context manager since at this point we already
        # are in a context. Worried about infinite recursion because we keep setting statuses for the next
        # pipelines? Since this method is only called when a pipeline moves from the "in progress" state to
        # a final state and the next pipeline is set to the "in progress" state, it should not trigger recursion.
        next_pipeline.status = PIPELINE_STATUS_IN_PROGRESS
        next_pipeline.save()

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(application__project__team__group__in=user_groups)


def pre_validate_steprun_update(serializer):
    """In case of an update to the status which sets the step to a final status, ensure the 'ended_at'
       field is set.
    """
    if (
        "status" in serializer.validated_data
        and serializer.validated_data["status"] in STEP_FINAL_STATUSES
        and "ended_at" not in serializer.validated_data
    ):
        serializer.validated_data["ended_at"] = datetime.now(tz=pytz.timezone(settings.TIME_ZONE))


class SCMStepRunViewSet(FilterViewMixin, AuditViewSet):
    model = SCMStepRun
    serializer_class = SCMStepRunSerializer

    def perform_update(self, serializer):
        pre_validate_steprun_update(serializer)
        serializer.save()

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        return super().get_queryset().filter(scm_pipeline_run__application__project__team__group__in=user_groups)


class SCMStepRunUpdateStatusView(UpdateAuditMixin):
    model = SCMStepRun
    serializer_class = SCMStepRunUpdateSerializer

    def perform_update(self, serializer):
        pre_validate_steprun_update(serializer)
        serializer.save()

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        return self.model.objects.exclude(deleted=True).filter(
            scm_pipeline_run__application__project__team__group__in=user_groups
        )


class SCMReleaseViewSet(FilterViewMixin, ReadOnlyAuditViewMixin):
    model = SCMRelease
    serializer_class = SCMReleaseSerializer

    parameter_lookup_map = {"application": "scm_pipeline_runs__application"}

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        # Do select distinct because of the many to many relationship
        return (
            super()
            .get_queryset()
            .distinct()
            .filter(scm_pipeline_runs__application__project__team__group__in=user_groups)
        )


class ApplicationMetadataViewSet(AuditViewSet):
    model = ApplicationMetadata
    serializer_class = ApplicationMetadataSerializer
    lookup_field = "key"

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        kwargs = {
            "application__project__team__group__in": user_groups,
            "application__deleted": False,
            "application": self.kwargs["applications_pk"],
            "deleted": False,
        }
        return super().get_queryset().filter(**kwargs)
