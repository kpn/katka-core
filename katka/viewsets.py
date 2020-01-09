from katka.auth import AuthType, has_full_access_scope
from katka.fields import username_on_model
from rest_framework import mixins, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .permissions import HasFullScope, IsGroupAuthenticated


class UserOrScopeViewSet(GenericViewSet):
    permission_classes = [IsGroupAuthenticated | HasFullScope]

    def initialize_request(self, request, *args, **kwargs):
        drf_request = super().initialize_request(request, *args, **kwargs)

        auth_type = AuthType.ANONYMOUS
        user_identifier = "anonymous"
        if getattr(drf_request, "user", None) is not None and not drf_request.user.is_anonymous:
            auth_type = AuthType.GROUPS
            user_identifier = request.user.username
        elif getattr(drf_request, "scopes", None) is not None:
            auth_type = AuthType.SCOPES
            user_identifier = "system_user"

        # set it on the django HttpRequest
        request.katka_auth_type = auth_type
        request.katka_user_identifier = user_identifier

        return drf_request

    def get_queryset(self):
        # do not call super().get_queryset() since it raises NotImplementedError
        queryset = self.model.objects.all()
        if self.request.katka_auth_type is AuthType.SCOPES:
            if has_full_access_scope(self.request):
                return queryset

            raise PermissionDenied("Missing full access scope")

        return self.get_user_restricted_queryset(queryset)

    def get_user_restricted_queryset(self, queryset):
        raise NotImplementedError  # noqa


class ReadOnlyAuditMixin(mixins.RetrieveModelMixin, mixins.ListModelMixin, UserOrScopeViewSet):
    model = None

    def get_queryset(self):
        return super().get_queryset().exclude(deleted=True)


class UpdateAuditMixin(mixins.UpdateModelMixin, UserOrScopeViewSet):
    model = None

    def update(self, request, *args, **kwargs):
        with username_on_model(self.model, request.katka_user_identifier):
            return super().update(request, *args, **kwargs)


class CreateAuditMixin(mixins.CreateModelMixin, UserOrScopeViewSet):
    def create(self, request, *args, **kwargs):
        with username_on_model(self.model, request.katka_user_identifier):
            return super().create(request, *args, **kwargs)


class DestroyAuditMixin(mixins.DestroyModelMixin, UserOrScopeViewSet):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = True

        with username_on_model(self.model, request.katka_user_identifier):
            instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AuditViewSet(CreateAuditMixin, UpdateAuditMixin, DestroyAuditMixin, ReadOnlyAuditMixin):
    pass


class FilterViewMixin:
    parameter_lookup_map = None

    """
    Uses the Serializer fields to construct GET Parameter filtering
    """

    def get_queryset(self):
        queryset = super().get_queryset()

        # Allow filtering on any field in serializer
        all_fields = self.model._meta.get_fields()
        filter_fields_lookup = {field.name: field.name for field in all_fields}
        filter_fields_keys = list(field.name for field in all_fields)

        # Also support a mapping from query parameter to django query field
        if self.parameter_lookup_map:
            filter_fields_keys += self.parameter_lookup_map.keys()
            filter_fields_lookup.update(self.parameter_lookup_map)

        # Loop through the keys to maintain proper order
        filters = {}
        for query_param in filter_fields_keys:
            django_lookup_field = filter_fields_lookup[query_param]
            value = self.request.query_params.get(query_param, None)
            if value is not None:
                filters[django_lookup_field] = value

        if filters:
            # Fetch distinct for all model fields, to prevent duplications due to SQL Joins
            queryset = queryset.distinct().filter(**filters)

        return queryset
