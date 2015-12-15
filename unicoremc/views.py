from django.views.generic import ListView, UpdateView

from controllers.base.views import ControllerViewMixin
from unicoremc.models import UserSettings
from unicoremc.forms import UserSettingsForm


class HomepageView(ControllerViewMixin, ListView):
    template_name = 'unicoremc/home.html'

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
