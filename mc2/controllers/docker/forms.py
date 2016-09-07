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
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    domain_urls = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(optional)'}),
        required=False)
    volume_needed = forms.BooleanField(
        required=False, label="Do you want storage?", initial=False,
        widget=forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]))
    volume_path = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False)
    webhook_token = forms.UUIDField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    postgres_db_needed = forms.BooleanField(
        required=False, label="Do you want to create postgres database?",
        initial=False,
        widget=forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]))
    postgres_db_username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    postgres_db_password = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    postgres_db_host = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    postgres_db_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = DockerController
        fields = (
            'name', 'marathon_cpus', 'marathon_mem', 'marathon_instances',
            'marathon_cmd', 'docker_image', 'marathon_health_check_path',
            'port', 'domain_urls', 'volume_needed', 'volume_path',
            'webhook_token', 'description', 'organization',
            'postgres_db_needed', 'postgres_db_name', 'postgres_db_host',
            'postgres_db_username', 'postgres_db_password')


class DockerControllerFormHelper(ControllerFormHelper):

    def __init__(self, data=None, files=None, instance=None,
                 prefix=None, initial={}):
        super(DockerControllerFormHelper, self).__init__(
            data, files, instance, prefix, initial)
        self.controller_form = DockerControllerForm(
            data, files, instance=instance, initial=initial)
