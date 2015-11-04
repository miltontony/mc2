from django.views.generic import ListView

from controllers.base.views import ControllerViewMixin


class HomepageView(ControllerViewMixin, ListView):
    template_name = 'unicoremc/home.html'

    def get_queryset(self):
        return self.get_controllers_queryset(self.request)
