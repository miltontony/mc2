from django import forms
from mc2.controllers.docker.models import DockerController
from mc2.controllers.base.forms import ControllerForm, ControllerFormHelper


class DockerControllerForm(ControllerForm):
    marathon_cmd = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'}))
    docker_image = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    marathon_health_check_path = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(optional)'}),
        required=False)
    port = forms.CharField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '(optional)'}),
        required=False)
    domain_urls = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(optional)'}),
        required=False)
    external_visibility = forms.BooleanField(
        required=False,
        initial=False,
        label="Should the URL be exposed to the outside world?",
        help_text=(
            "Disabling this field will remove this app from our load balancer "
            "and make it only accessible from inside the cluster."),
        widget=forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]))
    volume_needed = forms.BooleanField(
        required=False, label="Do you want storage?", initial=False,
        widget=forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]))
    volume_path = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False)
    webhook_token = forms.UUIDField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_port(self):
        return self.cleaned_data['port'] or None

    class Meta:
        model = DockerController
        fields = (
            'name', 'marathon_cpus', 'marathon_mem', 'marathon_instances',
            'marathon_cmd', 'docker_image', 'marathon_health_check_path',
            'port', 'domain_urls', 'volume_needed', 'volume_path',
            'webhook_token', 'description', 'organization',
            'postgres_db_needed', 'external_visibility')


class DockerControllerFormHelper(ControllerFormHelper):

    def __init__(self, data=None, files=None, instance=None,
                 prefix=None, initial={}):
        super(DockerControllerFormHelper, self).__init__(
            data, files, instance, prefix, initial)
        self.controller_form = DockerControllerForm(
            data, files, instance=instance, initial=initial)
