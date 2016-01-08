from functools import wraps

from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login
from django.utils.decorators import available_attrs

from mc2.organizations.models import Organization, ORGANIZATION_SESSION_KEY


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

    if org_id is None and request.user.is_superuser:
        return None

    try:
        if org_id is None:
            return Organization.objects.for_user(request.user).first()
        return Organization.objects.for_user(request.user).get(pk=org_id)
    except Organization.DoesNotExist:
        return None


def org_permission_required(perm, login_url=None, raise_exception=False):
    '''
    Decorator for views that checks that a user has the given permission
    for the active organization, redirecting to the login page if
    necessary.

    :params list or string perm:
        The permission(s) to check
    :params string login_url:
        The login url to redirect to if the check fails.
    :params bool raise_exception:
        Indicates whether to raise PermissionDenied if the check fails.
    '''

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if isinstance(perm, basestring):
                perms = (perm,)
            else:
                perms = perm

            user = request.user
            organization = active_organization(request)
            if organization and organization.has_perms(user, perms):
                return view_func(request, *args, **kwargs)
            elif not organization and user.has_perms(perms):
                # user permissions supersede user-organization permissions
                return view_func(request, *args, **kwargs)

            if raise_exception:
                raise PermissionDenied
            return redirect_to_login(request.build_absolute_uri(), login_url)
        return _wrapped_view
    return decorator
