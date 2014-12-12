from django import forms
from unicoremc.models import Project, Localisation
from django.forms import widgets


class ProjectForm(forms.ModelForm):
    ga_profile_id = forms.CharField()
    default_language = forms.ModelChoiceField(
        queryset=Localisation.objects.all(),
        empty_label=None,
        widget=widgets.RadioSelect())
    available_languages = forms.ModelMultipleChoiceField(
        queryset=Localisation.objects.all(),
        widget=widgets.CheckboxSelectMultiple)

    class Meta:
        model = Project
        fields = ('available_languages', 'default_language', 'ga_profile_id')
