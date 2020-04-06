from django.db.models import Q

from katka.models import Team


def get_teams(user):
    # Only show teams that are linked to a group that the user is part of
    # or that is connected directly to the team as a system user
    return Team.objects.filter(Q(group__in=user.groups.all()) | Q(sys_users=user))
