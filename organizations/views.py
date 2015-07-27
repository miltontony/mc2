from django.views.generic.base import View
from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from organizations.models import Organization


class OrganizationAdminMixin(View):

    @classmethod
    def as_view(cls):
        view = super(OrganizationAdminMixin, cls).as_view()
        return login_required(view)

    def get_queryset(self):
        return Organization.objects.for_admin_user(self.request.user)


class SelectOrganizationView(OrganizationAdminMixin, ListView):
    template_name = 'organizations/organization_select.html'
    context_object_name = 'organizations'
    allow_empty = False

    def dispatch(self, *args, **kwargs):
        try:
            [organization] = self.get_queryset()
            return redirect('organizations:admin', organization.slug)
        except ValueError:
            return super(SelectOrganizationView, self).dispatch(
                *args, **kwargs)


class OrganizationActionsView(OrganizationAdminMixin, DetailView):
    template_name = 'organizations/organization_admin.html'
    context_object_name = 'organization'


class OrganizationEditView(OrganizationAdminMixin, UpdateView):
    template_name = 'organizations/organization_detail.html'
    context_object_name = 'organization'
    fields = ('name', )

    def get_success_url(self):
        return reverse('organizations:admin', args=(self.object.slug, ))
