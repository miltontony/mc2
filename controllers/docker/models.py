from django.db import models

from controllers.base.models import Controller


class DockerController(Controller):
    docker_image = models.CharField(max_length=256)
    marathon_health_check_path = models.CharField(
        max_length=255, blank=True, null=True)
    port = models.PositiveIntegerField(default=0)

    def get_marathon_app_data(self):
        app_data = {
            "id": self.app_id,
            "cmd": self.marathon_cmd,
            "cpus": self.marathon_cpus,
            "mem": self.marathon_mem,
            "instances": self.marathon_instances,
            "container": {
                "type": "DOCKER",
                "docker": {
                    "image": self.docker_image,
                    "forcePullImage": True,
                    "network": "BRIDGE",
                }
            }
        }

        if self.port:
            app_data.update({
                "portMappings": [{"containerPort": self.port, "hostPort": 0}]
            })

        if self.marathon_health_check_path:
            app_data.update({
                "ports": [0],
                "healthChecks": [{
                    "gracePeriodSeconds": 3,
                    "intervalSeconds": 10,
                    "maxConsecutiveFailures": 3,
                    "path": self.marathon_health_check_path,
                    "portIndex": 0,
                    "protocol": "HTTP",
                    "timeoutSeconds": 5
                }]
            })

        return app_data
