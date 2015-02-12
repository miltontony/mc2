from django import forms
from unicoremc.models import Project, Localisation
from django.forms import widgets


class ProjectForm(forms.ModelForm):
    ga_profile_id = forms.CharField(required=False)
    custom_dns = forms.CharField(
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

    class Meta:
        model = Project
        fields = (
            'available_languages', 'default_language', 'ga_profile_id',
            'custom_dns')
