from katka.models import Team
from katka.serializers import TeamSerializer
from katka.viewsets import AuditViewSet


class TeamViewSet(AuditViewSet):
    model = Team
    serializer_class = TeamSerializer
    lookup_field = 'public_identifier'
    lookup_value_regex = '[0-9a-f-]{36}'
