from django import forms
from unicoremc.models import Project, Localisation
from django.forms.widgets import CheckboxSelectMultiple, RadioSelect


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('available_languages', 'default_language')

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)

        self.fields["available_languages"].widget = CheckboxSelectMultiple()
        self.fields[
            "available_languages"].queryset = Localisation.objects.all()
        self.fields["default_language"].widget = RadioSelect()
        self.fields["default_language"].choices = [
            (l.pk, str(l)) for l in Localisation.objects.all()]
