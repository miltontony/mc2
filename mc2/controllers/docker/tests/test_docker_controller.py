import pytest
import responses
from django.conf import settings
from django.contrib.auth.models import User
from hypothesis import given
from hypothesis.strategies import text, random_module, lists, just

from mc2.controllers.docker.tests.hypothesis_helper import (
    models, DEFAULT_VALUE)

from mc2.controllers.base.models import EnvVariable, MarathonLabel
from mc2.controllers.base.tests.base import ControllerBaseTestCase
from mc2.controllers.docker.models import DockerController


def add_envvars(controller):
    envvars = lists(models(EnvVariable, controller=just(controller)))
    return envvars.map(lambda _: controller)


def add_labels(controller):
    envvars = lists(models(MarathonLabel, controller=just(controller)))
    return envvars.map(lambda _: controller)


def docker_controller(with_envvars=True, with_labels=True, **kw):
    kw.setdefault("slug", text().map(
        lambda t: "".join(t.replace(":", "").split())))
    kw.setdefault("owner", models(User))
    controller = models(DockerController, controller_ptr=DEFAULT_VALUE, **kw)
    if with_envvars:
        controller = controller.flatmap(add_envvars)
    if with_labels:
        controller = controller.flatmap(add_labels)
    return controller


def filter_docker_data(docker, volume_needed):
    """
    Remove fields with default or unset values.
    """
    docker["portMappings"] = [pm for pm in docker["portMappings"]
                              if pm["containerPort"] != 0]
    if not docker["portMappings"]:
        docker.pop("portMappings")
    if not volume_needed:
        docker.pop("parameters")


def filter_app_data(appdata, **kw):
    """
    Remove fields with default or unset values.
    """
    if not appdata["cmd"]:
        appdata.pop("cmd")
    if not appdata["healthChecks"][0]["path"]:
        appdata.pop("healthChecks")
        appdata.pop("ports")
    if not appdata["env"]:
        appdata.pop("env")
    filter_docker_data(appdata["container"]["docker"], **kw)


@pytest.mark.django_db
class DockerControllerTestCase(ControllerBaseTestCase):
    fixtures = ['test_users.json', 'test_social_auth.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')
        self.maxDiff = None

    @given(_r=random_module(), controller=docker_controller())
    def test_get_marathon_app_data_h(self, _r, controller):

        app_data = {
            "id": controller.app_id,
            "cpus": controller.marathon_cpus,
            "mem": controller.marathon_mem,
            "instances": controller.marathon_instances,
            "cmd": controller.marathon_cmd,
            "labels": {
                "domain": u"{}.{} {}".format(controller.app_id,
                                             settings.HUB_DOMAIN,
                                             controller.domain_urls).strip(),
                "name": controller.name,
            },
            "container": {
                "type": "DOCKER",
                "docker": {
                    "image": controller.docker_image,
                    "forcePullImage": True,
                    "network": "BRIDGE",
                    "portMappings": [{
                        "containerPort": controller.port,
                        "hostPort": 0,
                    }],
                    "parameters": [
                        {"key": "volume-driver", "value": "xylem"},
                        {
                            "key": "volume",
                            "value": u"%s_media:%s" % (
                                controller.app_id,
                                controller.volume_path or
                                settings.MARATHON_DEFAULT_VOLUME_PATH),
                        },
                    ],
                },
            },
            "ports": [0],
            "healthChecks": [{
                "gracePeriodSeconds": 3,
                "intervalSeconds": 10,
                "maxConsecutiveFailures": 3,
                "path": controller.marathon_health_check_path,
                "portIndex": 0,
                "protocol": "HTTP",
                "timeoutSeconds": 5
            }],
            "env": {e.key: e.value for e in controller.env_variables.all()},
        }
        for label in controller.label_variables.all():
            app_data["labels"][label.name] = label.value

        filter_app_data(app_data, volume_needed=controller.volume_needed)

        self.assertEquals(app_data, controller.get_marathon_app_data())

    @given(_r=random_module(), controller=docker_controller())
    def test_from_marathon_app_data_h(self, _r, controller):

        orig_data = controller.get_marathon_app_data()
        new_controller = DockerController.from_marathon_app_data(
            controller.owner, orig_data)
        new_data = new_controller.get_marathon_app_data()
        self.assertEqual(orig_data, new_data)

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
                                            custom_urls),
                "name": "Test App",
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
                                            custom_urls),
                "name": "Test App"
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
                                            custom_urls),
                "name": "Test App",
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

        controller.volume_needed = True
        controller.volume_path = "/deploy/media/"
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
                                            custom_urls),
                "name": "Test App",
            },
            "container": {
                "type": "DOCKER",
                "docker": {
                    "image": "docker/image",
                    "forcePullImage": True,
                    "network": "BRIDGE",
                    "portMappings": [{"containerPort": 1234, "hostPort": 0}],
                    "parameters": [
                        {"key": "volume-driver", "value": "xylem"},
                        {
                            "key": "volume",
                            "value":
                                "%s_media:/deploy/media/" % controller.app_id
                        }]
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

        controller.volume_path = ""
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
                                            custom_urls),
                "name": "Test App",
            },
            "container": {
                "type": "DOCKER",
                "docker": {
                    "image": "docker/image",
                    "forcePullImage": True,
                    "network": "BRIDGE",
                    "portMappings": [{"containerPort": 1234, "hostPort": 0}],
                    "parameters": [
                        {"key": "volume-driver", "value": "xylem"},
                        {
                            "key": "volume",
                            "value":
                                "%s_media:%s" % (
                                    controller.app_id,
                                    settings.MARATHON_DEFAULT_VOLUME_PATH)
                        }]
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

    def test_get_marathon_app_data_with_env(self):
        controller = DockerController.objects.create(
            name='Test App',
            owner=self.user,
            marathon_cmd='ping',
            docker_image='docker/image',
        )
        self.mk_env_variable(controller)

        self.assertEquals(controller.get_marathon_app_data(), {
            "id": controller.app_id,
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "cmd": "ping",
            "env": {"TEST_KEY": "a test value"},
            "labels": {
                "domain": "{}.{}".format(controller.app_id,
                                         settings.HUB_DOMAIN),
                "name": "Test App",
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

    def test_get_marathon_app_data_with_app_labels(self):
        controller = DockerController.objects.create(
            name='Test App',
            owner=self.user,
            marathon_cmd='ping',
            docker_image='docker/image',
        )
        self.mk_env_variable(controller)
        self.mk_labels_variable(controller)

        self.assertEquals(controller.get_marathon_app_data(), {
            "id": controller.app_id,
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "cmd": "ping",
            "env": {"TEST_KEY": "a test value"},
            "labels": {
                "domain": "{}.{}".format(controller.app_id,
                                         settings.HUB_DOMAIN),
                "name": "Test App",
                "TEST_LABELS_NAME": 'a test label value'
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

    @responses.activate
    def test_marathon_cmd_optional(self):
        controller = DockerController.objects.create(
            name='Test App',
            owner=self.user,
            docker_image='docker/image',
        )

        self.assertEquals(controller.get_marathon_app_data(), {
            "id": controller.app_id,
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "labels": {
                "domain": "{}.{}".format(controller.app_id,
                                         settings.HUB_DOMAIN),
                "name": "Test App",
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
