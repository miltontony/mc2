import json

import pytest
import responses
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from hypothesis import given, settings as hsettings
from hypothesis.extra.django import TestCase
from hypothesis.extra.django.models import models, default_value
from hypothesis.strategies import text, random_module, lists, just

from mc2.controllers.base.models import EnvVariable, MarathonLabel
from mc2.controllers.base.tests.base import ControllerBaseTestCase
from mc2.controllers.docker.models import DockerController
from mc2.organizations.models import Organization


def add_envvars(controller):
    """
    Generate some EnvVariable models for the given controller.

    We discard these once we've made them because they're in the database.
    """
    envvars = lists(models(EnvVariable, controller=just(controller)))
    return envvars.map(lambda _: controller)


def add_labels(controller):
    """
    Generate some MarathonLabel models for the given controller.

    We discard these once we've made them because they're in the database.
    """
    labels = lists(models(MarathonLabel, controller=just(controller)))
    return labels.map(lambda _: controller)


def docker_controller(with_envvars=True, with_labels=True, **kw):
    """
    Generate a DockerController model with (optional) envvars and labels.
    """
    # The slug is used in places where whitespace and colons are problematic,
    # so we remove them from the generated value.
    # TODO: Build a proper SlugField strategy.
    # TODO: Figure out why the field validation isn't being applied.
    slug = text().map(lambda t: "".join(t.replace(":", "").split()))
    kw.setdefault("slug", slug)

    kw.setdefault("owner", models(User, is_active=just(True)))
    kw.setdefault("organization", models(Organization, slug=slug))
    # The model generator sees `controller_ptr` (from the PolymorphicModel
    # magic) as a mandatory field and objects if we don't provide a value for
    # it.
    controller = models(DockerController, controller_ptr=default_value, **kw)
    if with_envvars:
        controller = controller.flatmap(add_envvars)
    if with_labels:
        controller = controller.flatmap(add_labels)
    return controller


def check_and_clear_appdata(appdata, controller):
    """
    Assert that appdata is correct and clear it.

    Because there are a bunch of separate checks for different parts of the
    data, we remove each thing we check as we check it. If we don't have an
    empty dict at the end, there's something unexpected in the data.

    We do it this way instead of generating a big dict to compare against so
    that we don't end up with two copies of the same logic.
    """
    assert appdata.pop("id") == controller.app_id
    assert appdata.pop("cpus") == controller.marathon_cpus
    assert appdata.pop("mem") == controller.marathon_mem
    assert appdata.pop("instances") == controller.marathon_instances
    check_and_remove_optional(appdata, "cmd", controller.marathon_cmd)
    check_and_remove_docker(appdata, controller)
    check_and_remove_health(appdata, controller)
    check_and_remove_env(appdata, controller)
    check_and_remove_labels(appdata, controller)
    assert appdata == {}


def check_and_remove_docker(appdata, controller):
    """
    Assert that the docker container data is correct and remove it.
    """
    container = appdata.pop("container")
    assert container.pop("type") == "DOCKER"
    docker = container.pop("docker")
    assert docker.pop("image") == controller.docker_image
    assert docker.pop("forcePullImage") is True
    assert docker.pop("network") == "BRIDGE"
    if controller.port:
        assert docker.pop("portMappings") == [
            {"containerPort": controller.port, "hostPort": 0}]
    if controller.volume_needed:
        volume = u"%s_media:%s" % (
            controller.app_id,
            controller.volume_path or settings.MARATHON_DEFAULT_VOLUME_PATH)
        assert sorted(docker.pop("parameters")) == sorted([
            {"key": "volume-driver", "value": "xylem"},
            {"key": "volume", "value": volume},
        ])
    assert docker == {}
    assert container == {}


def check_and_remove_health(appdata, controller):
    """
    Assert that the health check data is correct and remove it.
    """
    if controller.marathon_health_check_path:
        assert appdata.pop("ports") == [0]
        assert appdata.pop("healthChecks") == [{
            "gracePeriodSeconds": 60,
            "intervalSeconds": 10,
            "maxConsecutiveFailures": 3,
            "path": controller.marathon_health_check_path,
            "portIndex": 0,
            "protocol": "HTTP",
            "timeoutSeconds": 20,
        }]
    assert "ports" not in appdata
    assert "healthChecks" not in appdata


def check_and_remove_env(appdata, controller):
    """
    Assert that the correct envvars are in appdata and remove them.
    """
    env_variables = controller.env_variables.all()
    if env_variables:
        # We may have duplicate keys in here, but hopefully the database always
        # return the objects in the same order.
        assert appdata.pop("env") == {ev.key: ev.value for ev in env_variables}
    assert "env" not in appdata


def check_and_remove_labels(appdata, controller):
    """
    Assert that the correct labels are in appdata and remove them.
    """
    labels = appdata.pop("labels")
    assert labels.pop("name") == controller.name
    domains = [u".".join([controller.app_id, settings.HUB_DOMAIN])]
    domains.extend(controller.domain_urls.split())
    assert sorted(labels.pop("domain").split()) == sorted(domains)
    # We may have duplicate keys in here, but hopefully the database always
    # return the objects in the same order.
    lvs = {lv.name: lv.value for lv in controller.label_variables.all()}
    assert labels == lvs


def check_and_remove_optional(appdata, field, value):
    """
    Assert that the given field has the correct value or is missing if unset.
    """
    if value:
        assert appdata.pop(field) == value
    assert field not in appdata


@pytest.mark.django_db
class DockerControllerHypothesisTestCase(TestCase):
    """
    Hypothesis tests for the DockerController model.

    These need to have the health checks disabled because Django model
    generation is very slow and occasionally fails the slow data generation
    check.
    """

    @hsettings(perform_health_check=False)
    @given(_r=random_module(), controller=docker_controller())
    def test_get_marathon_app_data(self, _r, controller):
        """
        Suitable app_data is built for any combination of model parameters.
        """
        app_data = controller.get_marathon_app_data()
        check_and_clear_appdata(app_data, controller)

    @hsettings(perform_health_check=False)
    @given(_r=random_module(), controller=docker_controller())
    def test_from_marathon_app_data(self, _r, controller):
        """
        A model imported from app_data generates the same app_data as the model
        it was imported from.
        """
        app_data = controller.get_marathon_app_data()
        new_controller = DockerController.from_marathon_app_data(
            controller.owner, controller.organization, app_data)
        assert app_data == new_controller.get_marathon_app_data()

    @hsettings(perform_health_check=False, max_examples=50)
    @given(_r=random_module(), controller=docker_controller(), name=text())
    def test_from_marathon_app_data_with_name(self, _r, controller, name):
        """
        A model imported from app_data generates the same app_data as the model
        it was imported from, but with the name field overridden.

        We limit the number of examples we generate because we don't need
        hundreds of examples to verify that this behaviour is correct.
        """
        app_data = controller.get_marathon_app_data()
        new_controller = DockerController.from_marathon_app_data(
            controller.owner, controller.organization, app_data, name=name)
        assert new_controller.name == name

        app_data_with_name = json.loads(json.dumps(app_data))
        app_data_with_name["labels"]["name"] = name
        assert app_data_with_name == new_controller.get_marathon_app_data()

    @hsettings(perform_health_check=False, max_examples=50)
    @given(_r=random_module(), controller=docker_controller(), name=text())
    def test_hidden_import_view(self, _r, controller, name):
        """
        A model imported through the hidden view generates the same app_data
        as the model it was imported from, but with the name field overridden.

        We limit the number of examples we generate because we don't need
        hundreds of examples to verify that this behaviour is correct.
        """
        app_data = controller.get_marathon_app_data()
        user = controller.owner
        user.set_password("password")  # So we can log in.
        user.save()
        client = Client()
        assert client.login(username=user.username, password="password")
        with responses.RequestsMock() as rsps:
            # If the Marathon request hasn't occurred by the time this context
            # is closed then the test will fail.
            rsps.add(
                responses.POST, '%s/v2/apps' % settings.MESOS_MARATHON_HOST,
                body="{}", content_type="application/json", status=201)
            resp = client.post(
                reverse('controllers.docker:hidden_import'),
                {"name": name, "app_data": json.dumps(app_data)})
        assert resp.status_code == 302

        new_controller = DockerController.objects.exclude(
            pk=controller.pk).get()
        assert new_controller.name == name

        app_data_with_name = json.loads(json.dumps(app_data))
        app_data_with_name["labels"]["name"] = name
        assert app_data_with_name == new_controller.get_marathon_app_data()


@pytest.mark.django_db
class DockerControllerTestCase(ControllerBaseTestCase):
    fixtures = ['test_users.json', 'test_social_auth.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')
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
                "gracePeriodSeconds": 60,
                "intervalSeconds": 10,
                "maxConsecutiveFailures": 3,
                "path": '/health/path/',
                "portIndex": 0,
                "protocol": "HTTP",
                "timeoutSeconds": 20
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
                "gracePeriodSeconds": 60,
                "intervalSeconds": 10,
                "maxConsecutiveFailures": 3,
                "path": '/health/path/',
                "portIndex": 0,
                "protocol": "HTTP",
                "timeoutSeconds": 20
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
                "gracePeriodSeconds": 60,
                "intervalSeconds": 10,
                "maxConsecutiveFailures": 3,
                "path": '/health/path/',
                "portIndex": 0,
                "protocol": "HTTP",
                "timeoutSeconds": 20
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

    @responses.activate
    def test_get_marathon_app_data_using_health_timeout_strings(self):
        controller = DockerController.objects.create(
            name='Test App',
            owner=self.user,
            marathon_cmd='ping',
            docker_image='docker/image',
            marathon_health_check_path='/health/path/',
            port=1234,
        )

        custom_urls = "testing.com url.com"
        controller.domain_urls += custom_urls
        with self.settings(
            MESOS_DEFAULT_GRACE_PERIOD_SECONDS='600',
            MESOS_DEFAULT_INTERVAL_SECONDS='100',
                MESOS_DEFAULT_TIMEOUT_SECONDS='200'):
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
                        "portMappings": [
                            {"containerPort": 1234, "hostPort": 0}],
                    }
                },
                "ports": [0],
                "healthChecks": [{
                    "gracePeriodSeconds": 600,
                    "intervalSeconds": 100,
                    "maxConsecutiveFailures": 3,
                    "path": '/health/path/',
                    "portIndex": 0,
                    "protocol": "HTTP",
                    "timeoutSeconds": 200
                }]
            })
