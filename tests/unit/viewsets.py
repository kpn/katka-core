from katka.viewsets import UserOrScopeViewSet
from tests.unit.models import SimpleModel


class AlwaysAuthenticate:
    def __init__(self, scopes):
        self.scopes = scopes

    def __call__(self):
        """
        Authentication_classes is meant to be a list of classes, not instances, but we need a state
        (the scopes), so we pass an instance. This will allow 'creating' an instance.
        """
        return self

    def authenticate(self, request, **kwargs):
        request.scopes = self.scopes
        user = None
        if self.scopes is None:
            user = request._request.user

        return user, "token"


class ViewSet(UserOrScopeViewSet):
    model = SimpleModel

    def __init__(self, request, scopes, **kwargs):
        self.authentication_classes = [AlwaysAuthenticate(scopes)]
        self.request = self.initialize_request(request)
        super().__init__(**kwargs)
