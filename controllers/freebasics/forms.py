from controllers.docker.forms import DockerControllerForm
from controllers.freebasics.models import FreeBasicsController
from django import forms

TEMPLATE_CHOICES = (
    ("option1", "molo-tuneme"),
    ("option2", "molo-ndohyep"),
)


class FreeBasicsControllerForm(DockerControllerForm):
    selected_template = forms.ChoiceField(choices=TEMPLATE_CHOICES, widget=forms.RadioSelect())

    class Meta:
        model = FreeBasicsController
        fields = (
            'name', 'selected_template')
