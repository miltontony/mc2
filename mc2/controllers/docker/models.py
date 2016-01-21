from django.db import models
from mc2.controllers.base.models import Controller
from django.conf import settings


class DockerController(Controller):
    docker_image = models.CharField(max_length=256)
    marathon_health_check_path = models.CharField(
        max_length=255, blank=True, null=True)
    port = models.PositiveIntegerField(default=0)
    domain_urls = models.TextField(max_length=8000, default="")
    volume_needed = models.BooleanField(default=False)
    volume_path = models.CharField(max_length=255, blank=True, null=True)

    def get_marathon_app_data(self):
        app_data = super(DockerController, self).get_marathon_app_data()
        docker_dict = {
            "image": self.docker_image,
            "forcePullImage": True,
            "network": "BRIDGE",
        }

        if self.port:
            docker_dict.update({
                "portMappings": [{"containerPort": self.port, "hostPort": 0}]
            })

        parameters_dict = []
        if self.volume_needed:
            parameters_dict.append({"key": "volume-driver", "value": "xylem"})
            parameters_dict.append({
                "key": "volume",
                "value": "%(app_id)s_media:%(path)s" % {
                    'app_id': self.app_id,
                    'path':
                        self.volume_path or
                        settings.MARATHON_DEFAULT_VOLUME_PATH}})

        if parameters_dict:
            docker_dict.update({"parameters": parameters_dict})

        domains = "%(generic_domain)s %(custom)s" % {
            'generic_domain': self.get_generic_domain(),
            'custom': self.domain_urls
        }

        service_labels = {
            "domain": domains.strip(),
            "name": self.name,
        }

        app_data.update({
            "labels": service_labels,
            "container": {
                "type": "DOCKER",
                "docker": docker_dict
            }
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

    def to_dict(self):
        data = super(DockerController, self).to_dict()
        data.update({
            'port': self.port,
            'marathon_health_check_path': self.marathon_health_check_path
        })
        return data

    def get_generic_domain(self):
        return '%(app_id)s.%(hub)s' % {
            'app_id': self.app_id,
            'hub': settings.HUB_DOMAIN
        }
