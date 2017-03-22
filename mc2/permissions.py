from urlparse import urlparse

from django.db.models import Q
from django.conf import settings

from mc2.controllers.docker.models import DockerController


def get_app_id_from_domain(domain):
    index = domain.find(settings.HUB_DOMAIN)
    if not index == -1:
        return domain[:index - 1]
    return None


def org_permissions(user, service):
    if user and service:
        domain = urlparse(service).hostname
        app_id = get_app_id_from_domain(domain)
        if app_id:
            controller = DockerController.objects.filter(
                Q(domain_urls__contains=domain) | Q(slug=app_id)).first()
        else:
            controller = DockerController.objects.filter(
                domain_urls__contains=domain).first()

        # super users have universal access
        if user.is_superuser:
            return {
                'givenName': user.first_name,
                'email': user.email,
                'has_perm': True,
                'is_admin': True,
                'service_name': service,
                'groups': []}

        if controller:
            # org admins have super user access
            if controller.organization.has_admin(user) or \
                    controller.organization.has_app_admin(user):
                return {
                    'givenName': user.first_name,
                    'email': user.email,
                    'has_perm': True,
                    'is_admin': True,
                    'service_name': service,
                    'groups': []}

            # normal org users have non-super user access
            if controller.organization.users.filter(id=user.id).exists():
                return {
                    'givenName': user.first_name,
                    'email': user.email,
                    'has_perm': True,
                    'is_admin': False,
                    'service_name': service,
                    'groups': []}
    return {
        'givenName': user.first_name,
        'email': user.email,
        'has_perm': False,
        'is_admin': False,
        'service_name': service,
        'groups': []}
