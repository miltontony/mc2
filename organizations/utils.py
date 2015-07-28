from organization.models import Organization, ORGANIZATION_SESSION_KEY


def active_organization(request):
    '''
    Returns the active :py:class:`organizations.models.Organization`
    object for the current user. Returns None if the user is not
    logged in or active, or no organization has been set.

    :params :py:class:`django.http.HttpRequest` request:
        The current request
    :returns:
        :py:class:`organizations.models.Organization`
    '''
    if not request.user.is_authenticated():
        return None

    org_id = request.session.get(ORGANIZATION_SESSION_KEY)
    if org_id is None:
        return None

    try:
        return Organization.objects.for_user(request.user).get(pk=org_id)
    except Organization.DoesNotExist:
        return None
