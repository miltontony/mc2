from django.db import models

from controllers.docker.models import DockerController

TEMPLATE_CHOICES = ("molo-tuneme", "molo-ndohyep")


class FreeBasicsController(DockerController):
    selected_template = models.CharField(
        default=TEMPLATE_CHOICES[0], max_length=100, blank=False, null=False)
