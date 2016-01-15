from django.http import Http404
from django.views.generic.base import View, RedirectView
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.http import is_safe_url

from mc2.organizations.models import Organization, ORGANIZATION_SESSION_KEY
from mc2.organizations.forms import OrganizationFormHelper


class OrganizationAdminMixin(View):

    @classmethod
    def as_view(cls):
        view = super(OrganizationAdminMixin, cls).as_view()
        return login_required(view)

    def get_queryset(self):
        return Organization.objects.for_admin_user(self.request.user)


class SelectActiveOrganizationView(OrganizationAdminMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, slug, *args, **kwargs):
        try:
            organization = Organization.objects.for_user(
                self.request.user).get(slug=slug)
        except Organization.DoesNotExist:
            raise Http404
        self.request.session[ORGANIZATION_SESSION_KEY] = organization.pk

        redirect_url = self.request.GET.get('next', None)
        if redirect_url is None or not is_safe_url(redirect_url):
            return reverse('home')
        return redirect_url


class DeselectActiveOrganizationView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        self.request.session.pop(ORGANIZATION_SESSION_KEY, None)

        redirect_url = self.request.GET.get('next', None)
        if redirect_url is None or not is_safe_url(redirect_url):
            return reverse('home')
        return redirect_url


class EditOrganizationView(OrganizationAdminMixin, UpdateView):
    template_name = 'organization_detail.html'
    context_object_name = 'organization'
    form_class = OrganizationFormHelper

    def get_success_url(self):
        return reverse('organizations:edit', args=(self.object[0].slug,))
