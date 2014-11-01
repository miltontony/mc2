from django import forms
from unicoremc.models import Project, Localisation
from django.forms.widgets import CheckboxSelectMultiple


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('available_languages', )

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)

        self.fields["available_languages"].widget = CheckboxSelectMultiple()
        self.fields[
            "available_languages"].queryset = Localisation.objects.all()
