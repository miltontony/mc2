import pytest
import responses
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from controllers.base.tests.base import ControllerBaseTestCase
from controllers.base.models import publish_to_websocket
from controllers.docker.models import DockerController


@pytest.mark.django_db
class DockerControllerTestCase(ControllerBaseTestCase):
    fixtures = ['test_users.json', 'test_social_auth.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')
        post_save.disconnect(publish_to_websocket, sender=DockerController)
        self.maxDiff = None

    def test_get_marathon_app_data(self):
        controller = DockerController.objects.create(
            name='Test App',
            owner=self.user,
            marathon_cmd='ping',
            docker_image='docker/image',
        )

        custom_urls = "testing.com url.com"
        controller.domain_urls += custom_urls
        self.assertEquals(controller.get_marathon_app_data(), {
            "id": controller.app_id,
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "cmd": "ping",
            "labels": {
                "domain": "{}.{} {}".format(controller.app_id,
                                            settings.HUB_DOMAIN,
                                            custom_urls)
            },
            "container": {
                "type": "DOCKER",
                "docker": {
                    "image": "docker/image",
                    "forcePullImage": True,
                    "network": "BRIDGE",
                }
            }
        })

        controller.port = 1234
        controller.save()

        self.assertEquals(controller.get_marathon_app_data(), {
            "id": controller.app_id,
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "cmd": "ping",
            "labels": {
                "domain": "{}.{} {}".format(controller.app_id,
                                            settings.HUB_DOMAIN,
                                            custom_urls)
            },
            "container": {
                "type": "DOCKER",
                "docker": {
                    "image": "docker/image",
                    "forcePullImage": True,
                    "network": "BRIDGE",
                    "portMappings": [{"containerPort": 1234, "hostPort": 0}],
                }
            },
        })

        controller.marathon_health_check_path = '/health/path/'
        controller.save()

        self.assertEquals(controller.get_marathon_app_data(), {
            "id": controller.app_id,
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "cmd": "ping",
            "labels": {
                "domain": "{}.{} {}".format(controller.app_id,
                                            settings.HUB_DOMAIN,
                                            custom_urls)
            },
            "container": {
                "type": "DOCKER",
                "docker": {
                    "image": "docker/image",
                    "forcePullImage": True,
                    "network": "BRIDGE",
                    "portMappings": [{"containerPort": 1234, "hostPort": 0}],
                }
            },
            "ports": [0],
            "healthChecks": [{
                "gracePeriodSeconds": 3,
                "intervalSeconds": 10,
                "maxConsecutiveFailures": 3,
                "path": '/health/path/',
                "portIndex": 0,
                "protocol": "HTTP",
                "timeoutSeconds": 5
            }]
        })

    @responses.activate
    def test_to_dict(self):
        controller = DockerController.objects.create(
            name='Test App',
            owner=self.user,
            marathon_cmd='ping',
            docker_image='docker/image',
            port=1234,
            marathon_health_check_path='/health/path/'
        )
        self.assertEquals(controller.to_dict(), {
            'id': controller.id,
            'name': 'Test App',
            'app_id': controller.app_id,
            'state': 'initial',
            'state_display': 'Initial',
            'marathon_cmd': 'ping',
            'port': 1234,
            'marathon_health_check_path': '/health/path/',
        })
