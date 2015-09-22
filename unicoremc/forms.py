from django import forms
from unicoremc.models import Project, Localisation
from django.forms import widgets


class ProjectForm(forms.ModelForm):
    ga_profile_id = forms.CharField(required=False)
    frontend_custom_domain = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input-xxlarge'}))
    cms_custom_domain = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input-xxlarge'}))
    default_language = forms.ModelChoiceField(
        queryset=Localisation.objects.all(),
        empty_label="Unspecified",
        widget=widgets.RadioSelect(),
        required=False)
    available_languages = forms.ModelMultipleChoiceField(
        queryset=Localisation.objects.all(),
        widget=widgets.CheckboxSelectMultiple,
        required=False)
    marathon_cpus = forms.FloatField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input-small'}))
    marathon_mem = forms.FloatField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input-small'}))
    marathon_instances = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.TextInput(attrs={'class': 'input-small'}))
    marathon_health_check_path = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input-medium'})
    )

    class Meta:
        model = Project
        fields = (
            'available_languages', 'default_language', 'ga_profile_id',
            'frontend_custom_domain', 'cms_custom_domain', 'marathon_cpus',
            'marathon_mem', 'marathon_instances', 'marathon_health_check_path',
            'docker_cmd', 'custom_frontend_settings')
