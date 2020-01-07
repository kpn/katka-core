from katka.viewsets import UserOrScopeViewSet
from tests.unit.models import SimpleModel


class ViewSet(UserOrScopeViewSet):
    model = SimpleModel

    def __init__(self, request, **kwargs):
        self.request = self.initialize_request(request)
        super().__init__(**kwargs)
