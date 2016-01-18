import logging

from django.views.generic import ListView, UpdateView
from django.contrib.auth import login

from mama_cas.views import LoginView
from mama_cas.utils import redirect
from mama_cas.models import ServiceTicket

from mc2.controllers.base.views import ControllerViewMixin
from mc2.models import UserSettings
from mc2.forms import UserSettingsForm

logger = logging.getLogger(__name__)


class HomepageView(ControllerViewMixin, ListView):
    template_name = 'mc2/home.html'

    def get_queryset(self):
        return self.get_controllers_queryset(self.request)


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
