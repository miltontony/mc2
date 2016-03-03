import logging

from django.views.generic import ListView, UpdateView
from django.contrib.auth import login
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from mama_cas.views import LoginView
from mama_cas.utils import redirect
from mama_cas.utils import to_bool
from mama_cas.models import ServiceTicket

from mc2.controllers.base.views import ControllerViewMixin
from mc2.models import UserSettings
from mc2.forms import UserSettingsForm
from mc2.organizations.utils import active_organization

logger = logging.getLogger(__name__)


class HomepageView(ControllerViewMixin, ListView):
    template_name = 'mc2/home.html'

    def get_context_data(self, *args, **kwargs):
        context = super(HomepageView, self).get_context_data(*args, **kwargs)
        active_org = active_organization(self.request)
        if active_org:
            context.update(
                {'is_admin': active_org.has_admin(self.request.user)})
        return context

    def get_queryset(self):
        return self.get_controllers_queryset(self.request).order_by('name')


class UserSettingsView(UpdateView):
    model = UserSettings
    form_class = UserSettingsForm

    def get_object(self, *args, **kwargs):
        return UserSettings.objects.get(user=self.request.user)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(UserSettingsView, self).form_valid(form)

    def get_success_url(self):
        return self.request.GET.get('next', '/')


class MC2LoginView(LoginView):

    def get(self, request, *args, **kwargs):
        self.request.session['service'] = self.request.GET.get('service')

        service = request.GET.get('service')
        renew = to_bool(request.GET.get('renew'))
        gateway = to_bool(request.GET.get('gateway'))

        if renew:
            logger.debug("Renew request received by credential requestor")
        elif gateway and service:
            logger.debug("Gateway request received by credential requestor")
            if request.user.is_authenticated():

                st = ServiceTicket.objects.create_ticket(service=service,
                                                         user=request.user)
                if self.warn_user():

                    return redirect('cas_warn', params={'service': service,
                                                        'ticket': st.ticket})
                return redirect(service, params={'ticket': st.ticket})

            else:
                return redirect(service)
        elif request.user.is_authenticated():
            if service:
                logger.debug("Service ticket request received by "
                             "credential requestor")
                st = ServiceTicket.objects.create_ticket(service=service,
                                                         user=request.user)
                if self.warn_user():
                    return redirect('cas_warn', params={'service': service,
                                                        'ticket': st.ticket})
                return redirect(service, params={'ticket': st.ticket})
            else:
                msg = _("You are logged in as %s") % request.user
                messages.success(request, msg)
                return redirect('home')
        return super(LoginView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(LoginView, self).get_context_data(*args, **kwargs)
        context.update({'service': self.request.session['service']})
        return context

    def form_valid(self, form):
        login(self.request, form.user)
        logger.info("Single sign-on session started for %s" % form.user)

        if form.cleaned_data.get('warn'):
            self.request.session['warn'] = True

        service = self.request.GET.get('service')
        if service:
            st = ServiceTicket.objects.create_ticket(service=service,
                                                     user=self.request.user,
                                                     primary=True)
            return redirect(service, params={'ticket': st.ticket})
        return redirect('home')
