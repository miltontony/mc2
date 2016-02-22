from mc2.controllers.base.views import ControllerCreateView, ControllerEditView
from mc2.controllers.docker.forms import DockerControllerFormHelper


class DockerControllerCreateView(ControllerCreateView):
    form_class = DockerControllerFormHelper
    template_name = 'docker_controller_edit.html'
    permissions = ['controllers.docker.add_dockercontroller']

    def form_valid(self, form):
        form.labels_formset.instance = form.controller_form.instance
        return super(DockerControllerCreateView, self).form_valid(self, form)


class DockerControllerEditView(ControllerEditView):
    form_class = DockerControllerFormHelper
    template_name = 'docker_controller_edit.html'
    permissions = ['controllers.docker.add_dockercontroller']
