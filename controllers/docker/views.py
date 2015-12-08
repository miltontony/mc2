from controllers.base.views import ControllerCreateView, ControllerEditView
from controllers.docker.forms import DockerControllerForm


class DockerControllerCreateView(ControllerCreateView):
    form_class = DockerControllerForm
    template_name = 'docker_controller_edit.html'
    permissions = ['controllers.docker.add_dockercontroller']


class DockerControllerEditView(ControllerEditView):
    form_class = DockerControllerForm
    template_name = 'docker_controller_edit.html'
    permissions = ['controllers.docker.add_dockercontroller']