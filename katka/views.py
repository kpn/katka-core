import json
import logging
from urllib.parse import urljoin

from django.conf import settings
from django.db import IntegrityError

from katka.constants import (
    PIPELINE_FINAL_STATUSES,
    PIPELINE_STATUS_IN_PROGRESS,
    PIPELINE_STATUS_INITIALIZING,
    PIPELINE_STATUS_QUEUED,
    PIPELINE_STATUS_SKIPPED,
)
from katka.exceptions import AlreadyExists, OutputNotValidError, ParentCommitMissing, PipelineRunnerError
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
    SCMStepRunAppendBuildInfoSerializer,
    SCMStepRunSerializer,
    SCMStepRunUpdateSerializer,
    TeamSerializer,
)
from katka.utils import get_teams
from katka.viewsets import AuditViewSet, FilterViewMixin, ReadOnlyAuditMixin, UpdateAuditMixin
from requests import HTTPError

log = logging.getLogger(__name__)


class TeamViewSet(FilterViewMixin, AuditViewSet):
    model = Team
    serializer_class = TeamSerializer
    lookup_field = "public_identifier"
    lookup_value_regex = "[0-9a-f-]{36}"
    parameter_lookup_map = {"application": "project__application"}

    def get_user_restricted_queryset(self, queryset):
        return get_teams(self.request.user)


class ProjectViewSet(FilterViewMixin, AuditViewSet):
    model = Project
    serializer_class = ProjectSerializer

    def get_user_restricted_queryset(self, queryset):
        user_teams = get_teams(self.request.user)
        return queryset.filter(team__in=user_teams)


class ApplicationViewSet(FilterViewMixin, AuditViewSet):
    model = Application
    serializer_class = ApplicationSerializer

    def get_user_restricted_queryset(self, queryset):
        user_teams = get_teams(self.request.user)
        return queryset.filter(project__team__in=user_teams)


class CredentialViewSet(FilterViewMixin, AuditViewSet):
    model = Credential
    serializer_class = CredentialSerializer

    def get_user_restricted_queryset(self, queryset):
        user_teams = get_teams(self.request.user)
        return queryset.filter(team__in=user_teams)


class CredentialSecretsViewSet(AuditViewSet):
    model = CredentialSecret
    serializer_class = CredentialSecretSerializer
    lookup_field = "key"

    def get_queryset(self):
        kwargs = {
            "credential__deleted": False,
            "credential": self.kwargs["credentials_pk"],
        }

        return super().get_queryset().filter(**kwargs)

    def get_user_restricted_queryset(self, queryset):
        user_teams = get_teams(self.request.user)
        return queryset.filter(credential__team__in=user_teams)


class SCMServiceViewSet(ReadOnlyAuditMixin):
    model = SCMService
    serializer_class = SCMServiceSerializer

    def get_user_restricted_queryset(self, queryset):
        return queryset  # no restrictions on user, this is global information


class SCMRepositoryViewSet(FilterViewMixin, AuditViewSet):
    model = SCMRepository
    serializer_class = SCMRepositorySerializer

    def get_user_restricted_queryset(self, queryset):
        user_teams = get_teams(self.request.user)
        return queryset.filter(credential__team__in=user_teams)


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
        application = serializer.validated_data["application"]
        if not self._can_create(application, serializer.validated_data.get("first_parent_hash")):
            raise ParentCommitMissing()

        # Upon pipeline creation, set to skipped if the application is inactive and no status is provided
        status = serializer.validated_data.get("status", None)
        if status is None and not application.active:
            serializer.validated_data["status"] = PIPELINE_STATUS_SKIPPED

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

    def get_user_restricted_queryset(self, queryset):
        user_teams = get_teams(self.request.user)
        return queryset.filter(application__project__team__in=user_teams)


class QueuedSCMPipelineRunViewSet(FilterViewMixin, ReadOnlyAuditMixin):
    model = SCMPipelineRun
    serializer_class = SCMPipelineRunSerializer

    def get_user_restricted_queryset(self, queryset):
        user_teams = get_teams(self.request.user)
        return queryset.filter(
            application__project__team__in=user_teams, status=PIPELINE_STATUS_QUEUED, scmrelease__isnull=True
        )


class SCMStepRunViewSet(FilterViewMixin, AuditViewSet):
    model = SCMStepRun
    serializer_class = SCMStepRunSerializer

    def get_user_restricted_queryset(self, queryset):
        user_teams = get_teams(self.request.user)
        return queryset.filter(scm_pipeline_run__application__project__team__in=user_teams)


class SCMStepRunUpdateStatusView(UpdateAuditMixin):
    model = SCMStepRun
    serializer_class = SCMStepRunUpdateSerializer

    def perform_update(self, serializer):
        # instead of saving the serializer, we call a remote endpoint
        self.call_endpoint(serializer)

    def call_endpoint(self, serializer):
        data = {
            "user": self.request.user.username,
            "step": {
                "public_identifier": str(serializer.instance.public_identifier),
                "status": serializer.validated_data["status"],
            },
        }
        session = settings.PIPELINE_RUNNER_SESSION
        url = urljoin(settings.PIPELINE_RUNNER_BASE_URL, settings.PIPELINE_UPDATE_STEP_EP)
        response = session.post(url, json=data)

        try:
            response.raise_for_status()
        except HTTPError:
            log.exception("Failed to update the step via the pipeline runner")
            raise PipelineRunnerError

    def get_user_restricted_queryset(self, queryset):
        user_groups = self.request.user.groups.all()
        return queryset.filter(scm_pipeline_run__application__project__team__group__in=user_groups)


class SCMStepRunAppendBuildInfoView(UpdateAuditMixin):
    model = SCMStepRun
    serializer_class = SCMStepRunAppendBuildInfoSerializer

    def perform_update(self, serializer):
        # instead of saving the serializer, we call a remote endpoint
        self.call_endpoint(serializer)

    def _build_data_params(self, serializer):
        data = {
            "user": self.request.user.username,
            "step": {
                "public_identifier": str(serializer.instance.public_identifier),
                "status": serializer.validated_data["status"],
            },
        }
        current_output = None
        if serializer.instance.output:
            try:
                current_output = json.loads(serializer.instance.output)
            except json.decoder.JSONDecodeError as e:
                raise OutputNotValidError(e)
        # "null" string is a valid json. In case we have null, replace with empty dict
        current_output = current_output if current_output else {}
        new_values_for_fields = {
            "build_number": serializer.validated_data["build_number"],
            "build_result": serializer.validated_data["build_result"],
            "comment": serializer.validated_data["comment"],
        }
        current_output.update(new_values_for_fields)
        data["step"]["output"] = json.dumps(current_output)
        return data

    def call_endpoint(self, serializer):

        data = self._build_data_params(serializer)
        session = settings.PIPELINE_RUNNER_SESSION
        url = urljoin(settings.PIPELINE_RUNNER_BASE_URL, settings.PIPELINE_UPDATE_STEP_EP)
        response = session.post(url, json=data)

        try:
            response.raise_for_status()
        except HTTPError:
            log.exception("Failed to update the step via the pipeline runner")
            raise PipelineRunnerError

    def get_user_restricted_queryset(self, queryset):
        user_teams = get_teams(self.request.user)
        return queryset.filter(scm_pipeline_run__application__project__team__in=user_teams)


class SCMReleaseViewSet(FilterViewMixin, ReadOnlyAuditMixin):
    model = SCMRelease
    serializer_class = SCMReleaseSerializer

    parameter_lookup_map = {"application": "scm_pipeline_runs__application", "pipeline_run": "scm_pipeline_runs"}

    def get_user_restricted_queryset(self, queryset):
        user_teams = get_teams(self.request.user)
        # Do select distinct because of the many to many relationship
        return queryset.distinct().filter(scm_pipeline_runs__application__project__team__in=user_teams)


class ApplicationMetadataViewSet(AuditViewSet):
    model = ApplicationMetadata
    serializer_class = ApplicationMetadataSerializer
    lookup_field = "key"
    lookup_value_regex = r"[^/]+"

    def get_queryset(self):
        kwargs = {
            "application__deleted": False,
            "application": self.kwargs["applications_pk"],
            "deleted": False,
        }

        return super().get_queryset().filter(**kwargs)

    def get_user_restricted_queryset(self, queryset):
        user_teams = get_teams(self.request.user)
        return queryset.filter(application__project__team__in=user_teams)
