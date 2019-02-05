from katka.constants import STATUS_INACTIVE
from katka.fields import username_on_model
from rest_framework import status, viewsets
from rest_framework.response import Response


class AuditViewSet(viewsets.ModelViewSet):
    model = None

    def get_queryset(self):
        return self.model.objects.exclude(status=STATUS_INACTIVE)

    def create(self, request, *args, **kwargs):
        with username_on_model(self.model, request.user.username):
            return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        with username_on_model(self.model, request.user.username):
            return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = STATUS_INACTIVE

        with username_on_model(self.model, request.user.username):
            instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
