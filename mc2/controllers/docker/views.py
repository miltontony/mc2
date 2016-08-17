from django.shortcuts import get_object_or_404
from mc2.controllers.base.views import (
    ControllerCreateView, ControllerEditView, ControllerCloneView)
from mc2.controllers.docker.forms import DockerControllerFormHelper
from mc2.controllers.docker.models import DockerController


class DockerControllerCreateView(ControllerCreateView):
    form_class = DockerControllerFormHelper
    template_name = 'docker_controller_edit.html'
    permissions = ['controllers.docker.add_dockercontroller']


class DockerControllerEditView(ControllerEditView):
    form_class = DockerControllerFormHelper
    template_name = 'docker_controller_edit.html'
    permissions = ['controllers.docker.add_dockercontroller']


class DockerControllerCloneView(ControllerCloneView):
    form_class = DockerControllerFormHelper
    template_name = 'docker_controller_edit.html'
    permissions = ['controllers.docker.add_dockercontroller']

    def get_initial(self):
        initial = super(DockerControllerCloneView, self).get_initial()

        instance = get_object_or_404(
            DockerController, pk=self.kwargs.get('controller_pk'))

        initial.update({
            'docker_image': instance.docker_image,
            'marathon_health_check_path': instance.marathon_health_check_path,
            'port': instance.port,
            'volume_needed': instance.volume_needed,
            'volume_path': instance.volume_path,
        })
        return initial
