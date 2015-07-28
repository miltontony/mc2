from organization.models import Organization
from organizations.utils import active_organization


def org(request):
    if not request.user.is_authenticated():
        return {
            'organizations': [],
            'active_organization': None
        }

    return {
        'organizations': Organization.objects.for_user(request.user),
        'active_organization': active_organization(request)
    }
