import pytest
import responses
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from mc2.controllers.base.tests.base import ControllerBaseTestCase
from mc2.controllers.docker.models import DockerController, traefik_domains
from mc2.organizations.models import Organization, OrganizationUserRelation


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
        org = Organization.objects.create(name="Test Org", slug="test-org")
        OrganizationUserRelation.objects.create(
            user=self.user, organization=org)
        controller.organization = org
        controller.save()

        custom_urls = "testing.com url.com"
        controller.domain_urls += custom_urls
        domain_label = "{}.{} {}".format(
            controller.app_id, settings.HUB_DOMAIN, custom_urls)
        self.assertEquals(controller.get_marathon_app_data(), {
            "id": controller.app_id,
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "cmd": "ping",
            "backoffFactor": settings.MESOS_DEFAULT_BACKOFF_FACTOR,
            "backoffSeconds": settings.MESOS_DEFAULT_BACKOFF_SECONDS,
            "labels": {
                "domain": domain_label,
                "HAPROXY_GROUP": "external",
                "HAPROXY_0_VHOST": domain_label,
                "traefik.frontend.rule": traefik_domains(domain_label),
                "name": "Test App",
                "org": "test-org",
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

        domain_label = "{}.{} {}".format(
            controller.app_id, settings.HUB_DOMAIN, custom_urls)
        self.assertEquals(controller.get_marathon_app_data(), {
            "id": controller.app_id,
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "cmd": "ping",
            "backoffFactor": settings.MESOS_DEFAULT_BACKOFF_FACTOR,
            "backoffSeconds": settings.MESOS_DEFAULT_BACKOFF_SECONDS,
            "labels": {
                "domain": domain_label,
                "HAPROXY_GROUP": "external",
                "HAPROXY_0_VHOST": domain_label,
                "traefik.frontend.rule": traefik_domains(domain_label),
                "name": "Test App",
                "org": "test-org",
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

        domain_label = "{}.{} {}".format(
            controller.app_id, settings.HUB_DOMAIN, custom_urls)
        self.assertEquals(controller.get_marathon_app_data(), {
            "id": controller.app_id,
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "cmd": "ping",
            "backoffFactor": settings.MESOS_DEFAULT_BACKOFF_FACTOR,
            "backoffSeconds": settings.MESOS_DEFAULT_BACKOFF_SECONDS,
            "labels": {
                "domain": domain_label,
                "HAPROXY_GROUP": "external",
                "HAPROXY_0_VHOST": domain_label,
                "traefik.frontend.rule": traefik_domains(domain_label),
                "name": "Test App",
                "org": "test-org",
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

        domain_label = "{}.{} {}".format(
            controller.app_id, settings.HUB_DOMAIN, custom_urls)
        self.assertEquals(controller.get_marathon_app_data(), {
            "id": controller.app_id,
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "cmd": "ping",
            "backoffFactor": settings.MESOS_DEFAULT_BACKOFF_FACTOR,
            "backoffSeconds": settings.MESOS_DEFAULT_BACKOFF_SECONDS,
            "labels": {
                "domain": domain_label,
                "HAPROXY_GROUP": "external",
                "HAPROXY_0_VHOST": domain_label,
                "traefik.frontend.rule": traefik_domains(domain_label),
                "name": "Test App",
                "org": "test-org",
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

        domain_label = "{}.{} {}".format(
            controller.app_id, settings.HUB_DOMAIN, custom_urls)
        self.assertEquals(controller.get_marathon_app_data(), {
            "id": controller.app_id,
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "cmd": "ping",
            "backoffFactor": settings.MESOS_DEFAULT_BACKOFF_FACTOR,
            "backoffSeconds": settings.MESOS_DEFAULT_BACKOFF_SECONDS,
            "labels": {
                "domain": domain_label,
                "HAPROXY_GROUP": "external",
                "HAPROXY_0_VHOST": domain_label,
                "traefik.frontend.rule": traefik_domains(domain_label),
                "name": "Test App",
                "org": "test-org",
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

        domain_label = "{}.{}".format(controller.app_id, settings.HUB_DOMAIN)
        self.assertEquals(controller.get_marathon_app_data(), {
            "id": controller.app_id,
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "cmd": "ping",
            "backoffFactor": settings.MESOS_DEFAULT_BACKOFF_FACTOR,
            "backoffSeconds": settings.MESOS_DEFAULT_BACKOFF_SECONDS,
            "env": {"TEST_KEY": "a test value"},
            "labels": {
                "domain": domain_label,
                "HAPROXY_GROUP": "external",
                "HAPROXY_0_VHOST": domain_label,
                "traefik.frontend.rule": traefik_domains(domain_label),
                "name": "Test App",
                "org": "",
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

        domain_label = "{}.{}".format(controller.app_id, settings.HUB_DOMAIN)
        self.assertEquals(controller.get_marathon_app_data(), {
            "id": controller.app_id,
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "cmd": "ping",
            "backoffFactor": settings.MESOS_DEFAULT_BACKOFF_FACTOR,
            "backoffSeconds": settings.MESOS_DEFAULT_BACKOFF_SECONDS,
            "env": {"TEST_KEY": "a test value"},
            "labels": {
                "domain": domain_label,
                "HAPROXY_GROUP": "external",
                "HAPROXY_0_VHOST": domain_label,
                "traefik.frontend.rule": traefik_domains(domain_label),
                "name": "Test App",
                "TEST_LABELS_NAME": 'a test label value',
                "org": "",
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
    def test_get_marathon_app_data_with_postgres_db_needed(self):
        controller = DockerController.objects.create(
            name='Test App',
            owner=self.user,
            marathon_cmd='ping',
            docker_image='docker/image',
            postgres_db_needed=True,
        )

        self.mock_create_postgres_db(200, {
            'result': {
                'name': 'joes_db',
                'user': 'joe',
                'password': '1234',
                'host': 'localhost'}})

        domain_label = "{}.{}".format(controller.app_id, settings.HUB_DOMAIN)
        self.assertEquals(controller.get_marathon_app_data(), {
            "id": controller.app_id,
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "cmd": "ping",
            "backoffFactor": settings.MESOS_DEFAULT_BACKOFF_FACTOR,
            "backoffSeconds": settings.MESOS_DEFAULT_BACKOFF_SECONDS,
            "env": {
                "DATABASE_URL": u"postgres://joe:1234@localhost/joes_db"},
            "labels": {
                "domain": domain_label,
                "HAPROXY_GROUP": "external",
                "HAPROXY_0_VHOST": domain_label,
                "traefik.frontend.rule": traefik_domains(domain_label),
                "name": "Test App",
                "org": "",
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

        domain_label = "{}.{}".format(controller.app_id, settings.HUB_DOMAIN)
        self.assertEquals(controller.get_marathon_app_data(), {
            "id": controller.app_id,
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "backoffFactor": settings.MESOS_DEFAULT_BACKOFF_FACTOR,
            "backoffSeconds": settings.MESOS_DEFAULT_BACKOFF_SECONDS,
            "labels": {
                "domain": domain_label,
                "HAPROXY_GROUP": "external",
                "HAPROXY_0_VHOST": domain_label,
                "traefik.frontend.rule": traefik_domains(domain_label),
                "name": "Test App",
                "org": "",
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
            domain_label = "{}.{} {}".format(
                controller.app_id, settings.HUB_DOMAIN, custom_urls)
            self.assertEquals(controller.get_marathon_app_data(), {
                "id": controller.app_id,
                "cpus": 0.1,
                "mem": 128.0,
                "instances": 1,
                "cmd": "ping",
                "backoffFactor": settings.MESOS_DEFAULT_BACKOFF_FACTOR,
                "backoffSeconds": settings.MESOS_DEFAULT_BACKOFF_SECONDS,
                "labels": {
                    "domain": domain_label,
                    "HAPROXY_GROUP": "external",
                    "HAPROXY_0_VHOST": domain_label,
                    "traefik.frontend.rule": traefik_domains(domain_label),
                    "name": "Test App",
                    "org": "",
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

    @responses.activate
    def test_create_new_controller_with_no_port(self):
        org = Organization.objects.create(name="Foo Org", slug="foo-org")
        OrganizationUserRelation.objects.create(
            user=self.user, organization=org)

        self.client.login(username='testuser2', password='test')
        self.client.get(
            reverse('organizations:select-active', args=('foo-org',)))

        self.mock_create_marathon_app()
        self.mock_create_postgres_db(200, {
            'result': {
                'name': 'joes_db',
                'user': 'joe',
                'password': '1234',
                'host': 'localhost'}})

        data = {
            'name': 'Another test app',
            'docker_image': 'test/image',
            'postgres_db_needed': True,
            'env-TOTAL_FORMS': 0,
            'env-INITIAL_FORMS': 0,
            'env-MIN_NUM_FORMS': 0,
            'env-MAX_NUM_FORMS': 100,
            'label-TOTAL_FORMS': 0,
            'label-INITIAL_FORMS': 0,
            'label-MIN_NUM_FORMS': 0,
            'label-MAX_NUM_FORMS': 100,
            'link-TOTAL_FORMS': 0,
            'link-INITIAL_FORMS': 0,
            'link-MIN_NUM_FORMS': 0,
            'link-MAX_NUM_FORMS': 100,


        }

        response = self.client.post(reverse('controllers.docker:add'), data)
        self.assertEqual(response.status_code, 302)

        controller = DockerController.objects.all().last()
        self.assertEqual(controller.state, 'done')
        self.assertEqual(controller.name, 'Another test app')
        self.assertEqual(controller.organization.slug, 'foo-org')
        self.assertIsNone(controller.port)
