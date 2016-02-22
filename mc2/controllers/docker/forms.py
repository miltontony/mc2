from django import forms
from django.utils.translation import ugettext_lazy as _
from mc2.controllers.docker.models import DockerController, MarathonLabel
from mc2.controllers.base.forms import ControllerForm, ControllerFormHelper


class DockerControllerForm(ControllerForm):
    marathon_cmd = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'}))
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
    volume_needed = forms.BooleanField(
        required=False, label="Do you want storage?", initial=False,
        widget=forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]))
    volume_path = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False)

    class Meta:
        model = DockerController
        fields = (
            'name', 'marathon_cpus', 'marathon_mem', 'marathon_instances',
            'marathon_cmd', 'docker_image', 'marathon_health_check_path',
            'port', 'domain_urls', 'volume_needed', 'volume_path')

class MarathonLabelForm(forms.ModelForm):
    name = forms.RegexField(
        "^[0-9a-zA-Z_]+$", required=True, error_messages={
            'invalid':
                _("You did not enter a valid key. Please try again.")},
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    value = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = MarathonLabel
        fields = ('name', 'value')


MarathonLabelInlineFormSet = forms.inlineformset_factory(
    DockerController,
    MarathonLabel,
    form=MarathonLabelForm,
    extra=1,
    can_delete=True,
    can_order=False
)

class DockerControllerFormHelper(ControllerFormHelper):

    def __init__(self, data=None, files=None, instance=None,
                 prefix=None, initial={}):
        super(DockerControllerFormHelper, self).__init__(
            data, files, instance, prefix, initial)
        self.controller_form = DockerControllerForm(
            data, files, instance=instance)
        self.labels_formset = MarathonLabelInlineFormSet(
            data, files,
            instance=instance,
            prefix='labels')

        def __iter__(self):
            yield self.controller_form
            yield self.env_formset
            yield self.labels_formset
