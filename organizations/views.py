from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect

from organizations.models import Organization


class OrganizationView(TemplateView):

    @classmethod
    def as_view(cls):
        view = super(OrganizationView, cls).as_view()
        return login_required(view)


class SelectOrganizationView(OrganizationView):
    template_name = 'organizations/organization_select.html'

    def dispatch(self, *args, **kwargs):
        try:
            [organization] = Organization.objects.for_admin_user(
                self.request.user)
            return redirect('organizations:admin', organization.slug)
        except ValueError:
            return super(SelectOrganizationView, self).dispatch(
                *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OrganizationView, self).get_context_data(**kwargs)
        context['organizations'] = self.request.user.organization_set.all()
        return context


class OrganizationAdminView(OrganizationView):

    def dispatch(self, *args, **kwargs):
        try:
            self.organization = Organization.objects.for_admin_user(
                self.request.user).get(slug=kwargs['slug'])
        except Organization.DoesNotExist:
            raise Http404
        return super(OrganizationAdminView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OrganizationAdminView, self).get_context_data(**kwargs)
        context['organization'] = self.organization
        return context


class OrganizationActionsView(OrganizationAdminView):
    template_name = 'organizations/organization_admin.html'


class OrganizationEditView(UpdateView, OrganizationView):
    template_name = 'organizations/organization_detail.html'
    model = Organization
