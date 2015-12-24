from mc2.organizations.models import Organization
from mc2.organizations.utils import active_organization


def org(request):
    if not request.user.is_authenticated():
        return {
            'organizations': [],
            'active_organization': None,
            'is_active_organization_admin': False
        }

    active_org = active_organization(request)
    return {
        'organizations': Organization.objects.for_user(request.user),
        'active_organization': active_org,
        'is_active_organization_admin': (
            active_org and active_org.has_admin(request.user))
    }
