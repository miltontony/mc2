from django.db import models
from controllers.base.models import Controller


class DockerController(Controller):
    docker_image = models.CharField(max_length=256)
    marathon_health_check_path = models.CharField(
        max_length=255, blank=True, null=True)
    port = models.PositiveIntegerField(default=0)

    def get_marathon_app_data(self):
        docker_dict = {
            "image": self.docker_image,
            "forcePullImage": True,
            "network": "BRIDGE",
        }

        if self.port:
            docker_dict.update({
                "portMappings": [{"containerPort": self.port, "hostPort": 0}]
            })

        service_labels = {
            "domain": "{}.127.0.0.1.xip.io".format(self.app_id),
        }

        app_data = {
            "id": self.app_id,
            "cmd": self.marathon_cmd,
            "cpus": self.marathon_cpus,
            "mem": self.marathon_mem,
            "instances": self.marathon_instances,
            "labels": service_labels,
            "container": {
                "type": "DOCKER",
                "docker": docker_dict
            }
        }

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

    def to_dict(self):
        data = super(DockerController, self).to_dict()
        data.update({
            'port': self.port,
            'marathon_health_check_path': self.marathon_health_check_path
        })
        return data
