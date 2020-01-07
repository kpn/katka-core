from katka.auth import has_full_access_scope
from katka.models import Application, Credential, Project, SCMPipelineRun, SCMRepository, SCMService, Team
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
        if key == "does_not_exist":
            raise PermissionDenied(self.does_not_exist_message)

        return super().fail(key, **kwargs)


class TeamRelatedField(PrimaryKeyRelated403Field):
    does_not_exist_message = "Team does not exist or you are not a member of its group"

    def get_queryset(self):
        request = self.context["request"]
        queryset = Team.objects.filter(deleted=False)
        if not has_full_access_scope(request):
            queryset = queryset.filter(group__in=request.user.groups.all())

        return queryset


class ProjectRelatedField(PrimaryKeyRelated403Field):
    does_not_exist_message = "Project does not exist or is not linked to your team"

    def get_queryset(self):
        request = self.context["request"]
        queryset = Project.objects.filter(team__deleted=False, deleted=False)
        if not has_full_access_scope(request):
            queryset = queryset.filter(team__group__in=request.user.groups.all())

        return queryset


class CredentialRelatedField(PrimaryKeyRelated403Field):
    does_not_exist_message = "Credential or team does not exist or is not linked to your group"

    def get_queryset(self):
        request = self.context["request"]
        queryset = Credential.objects.filter(team__deleted=False, deleted=False)
        if not has_full_access_scope(request):
            queryset = queryset.filter(team__group__in=request.user.groups.all())

        return queryset


class SCMServiceRelatedField(PrimaryKeyRelated403Field):
    does_not_exist_message = "SCMService does not exist"

    def get_queryset(self):
        return SCMService.objects.filter(deleted=False)


class SCMRepositoryRelatedField(PrimaryKeyRelated403Field):
    does_not_exist_message = "SCMRepository does not exist"

    def get_queryset(self):
        return SCMRepository.objects.filter(scm_service__deleted=False, credential__deleted=False, deleted=False)


class ApplicationRelatedField(PrimaryKeyRelated403Field):
    does_not_exist_message = "Application does not exist or does not belong to your team"

    def get_queryset(self):
        request = self.context["request"]
        queryset = Application.objects.filter(project__team__deleted=False, project__deleted=False, deleted=False,)
        if not has_full_access_scope(request):
            queryset = queryset.filter(project__team__group__in=request.user.groups.all())

        return queryset


class SCMPipelineRunRelatedField(PrimaryKeyRelated403Field):
    does_not_exist_message = "SCM Pipeline Run does not exist or does not belong to your team"

    def get_queryset(self):
        request = self.context["request"]
        queryset = SCMPipelineRun.objects.filter(
            application__project__team__deleted=False,
            application__project__deleted=False,
            application__deleted=False,
            deleted=False,
        )
        if not has_full_access_scope(request):
            queryset = queryset.filter(application__project__team__group__in=request.user.groups.all())

        return queryset
