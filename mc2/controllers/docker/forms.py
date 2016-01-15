from django import forms
from mc2.controllers.docker.models import DockerController
from mc2.controllers.base.forms import ControllerForm


class DockerControllerForm(ControllerForm):
    docker_image = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    marathon_health_check_path = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False)
    port = forms.CharField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    domain_urls = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False)

    class Meta:
        model = DockerController
        fields = (
            'name', 'marathon_cpus', 'marathon_mem', 'marathon_instances',
            'marathon_cmd', 'docker_image', 'marathon_health_check_path',
            'port', 'domain_urls')
