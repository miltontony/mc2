from django.db import models
from mc2.controllers.docker.models import DockerController


class FreeBasicsController(DockerController):
    TEMPLATE_CHOICES = (
        ("option1", "molo-tuneme"),
        ("option2", "molo-ndohyep"),
    )
    TEMPLATE_MARATHON_CMD = {
        "option1": "./deploy/docker-entrypoint.sh tuneme tuneme.wsgi 8000",
        "option2": "./deploy/docker-entrypoint.sh bwise ndohyep.wsgi 8000"
    }
    DEFAULT_PORT = 8000
    selected_template = models.CharField(
        default=TEMPLATE_CHOICES[0][1], max_length=100, blank=False,
        null=False)
