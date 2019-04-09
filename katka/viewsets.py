from katka.fields import username_on_model
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class ReadOnlyAuditViewMixin(mixins.RetrieveModelMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    model = None

    def get_queryset(self):
        return self.model.objects.exclude(deleted=True)


class AuditViewSet(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   ReadOnlyAuditViewMixin):

    def create(self, request, *args, **kwargs):
        with username_on_model(self.model, request.user.username):
            return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        with username_on_model(self.model, request.user.username):
            return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = True

        with username_on_model(self.model, request.user.username):
            instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class FilterViewMixin:
    """
    Uses the Serializer fields to construct GET Parameter filtering
    """
    def get_queryset(self):
        queryset = super().get_queryset()

        related_fields = self.serializer_class.get_related_fields()

        filters = {}
        for param in related_fields:
            value = self.request.query_params.get(param, None)
            if value is not None:
                filters[param] = value

        if filters:
            queryset = queryset.filter(**filters)

        return queryset
