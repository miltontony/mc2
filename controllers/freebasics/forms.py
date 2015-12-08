from controllers.docker.forms import DockerControllerForm
from controllers.freebasics.models import FreeBasicsController
from django import forms
from django.forms.utils import ErrorList

TEMPLATE_CHOICES = (
    ("option1", "molo-tuneme"),
    ("option2", "molo-ndohyep"),
)

_TEMPLATE_MARATHON_CMD = {
    "option1": "./deploy/docker-entrypoint.sh tuneme tuneme.wsgi 8000",
    "option2": "./deploy/docker-entrypoint.sh bwise ndohyep.wsgi 8000"
}

DEFAULT_PORT = 8000


class FreeBasicsControllerForm(DockerControllerForm):
    selected_template = forms.ChoiceField(
        choices=TEMPLATE_CHOICES, widget=forms.RadioSelect)

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, instance=None):
        data = self._process_data(data)
        super(FreeBasicsControllerForm, self).__init__(data, files, auto_id,
                                                       prefix, initial,
                                                       error_class,
                                                       label_suffix,
                                                       empty_permitted,
                                                       instance)

    def _process_data(self, data):
        if data is not None:
            data = data.copy()
            data.appendlist('port', DEFAULT_PORT)
            data.appendlist('docker_image', self._get_docker_image_name(
                data['selected_template']))
            data.appendlist('marathon_cmd', self._get_marathon_cmd(
                data['selected_template']))

        return data

    def _get_docker_image_name(self, selection_id):
        return "universalcore/" + dict(TEMPLATE_CHOICES)[selection_id]

    def _get_marathon_cmd(self, selection_id):
        return _TEMPLATE_MARATHON_CMD[selection_id]

    class Meta(DockerControllerForm.Meta):
        model = FreeBasicsController
        fields = DockerControllerForm.Meta.fields + ('selected_template',)
