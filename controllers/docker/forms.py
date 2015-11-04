from django import forms
from controllers.docker.models import DockerController
from controllers.base.forms import ControllerForm


class DockerControllerForm(ControllerForm):
    docker_image = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-xxlarge'}))
    marathon_health_check_path = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-medium'}),
        required=False)

    class Meta:
        model = DockerController
        fields = (
            'name', 'marathon_cpus', 'marathon_mem', 'marathon_instances',
            'marathon_cmd', 'docker_image', 'marathon_health_check_path',
            'port')
