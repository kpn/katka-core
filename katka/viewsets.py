from katka.fields import username_on_model
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class ReadOnlyAuditViewMixin(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    model = None

    def get_queryset(self):
        return self.model.objects.exclude(deleted=True)


class UpdateAuditMixin(mixins.UpdateModelMixin, GenericViewSet):
    def update(self, request, *args, **kwargs):
        with username_on_model(self.model, request.user.username):
            return super().update(request, *args, **kwargs)


class AuditViewSet(mixins.CreateModelMixin, UpdateAuditMixin, mixins.DestroyModelMixin, ReadOnlyAuditViewMixin):
    def create(self, request, *args, **kwargs):
        with username_on_model(self.model, request.user.username):
            return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = True

        with username_on_model(self.model, request.user.username):
            instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


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
