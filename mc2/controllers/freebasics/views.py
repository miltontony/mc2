from mc2.controllers.base.views import ControllerCreateView, ControllerEditView
from mc2.controllers.freebasics.forms import FreeBasicsControllerForm


class FreeBasicsControllerCreateView(ControllerCreateView):
    form_class = FreeBasicsControllerForm
    template_name = 'freebasics_controller_edit.html'
    permissions = ['controllers.docker.add_dockercontroller']


class FreeBasicsControllerEditView(ControllerEditView):
    form_class = FreeBasicsControllerForm
    template_name = 'freebasics_controller_edit.html'
    permissions = ['controllers.docker.add_dockercontroller']
