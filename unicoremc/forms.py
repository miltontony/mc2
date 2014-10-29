from django import forms
from unicoremc.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('available_languages', )
