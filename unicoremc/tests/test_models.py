import pytest

from django.contrib.auth.models import User
from django.db.models.signals import post_save

from unicoremc.tests.base import UnicoremcTestCase
from unicoremc.models import Project, AppType, publish_to_websocket
from unicoremc import exceptions


@pytest.mark.django_db
class ModelsTestCase(UnicoremcTestCase):
    fixtures = ['test_users.json', 'test_social_auth.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')
        post_save.disconnect(publish_to_websocket, sender=Project)
        self.maxDiff = None

    def test_app_type_title(self):
        app_type = AppType._for(
            'gem', 'Girl Effect', 'unicore-cms',
            'universalcore/unicore-cms-gem')
        self.assertEquals(str(app_type), 'Girl Effect (unicore-cms)')

    def test_project_app_type(self):
        app_type = AppType._for(
            'gem', 'Girl Effect', 'unicore-cms',
            'universalcore/unicore-cms-gem')

        p = Project(
            country='ZA',
            owner=self.user)
        p.save()

        self.assertEquals(p.app_type, '')

        p = Project(
            application_type=app_type,
            country='ZA',
            owner=self.user)
        p.save()

        self.assertEquals(p.app_type, 'gem')

    def test_project_repos(self):
        p = self.mk_project()
        p2 = self.mk_project(
            project={'country': 'UK'},
            repo={
                'base_url': 'foo.com',
                'url': 'https://foo.com',
                'git_url': 'git://foo.com'},
            app_type={'name': 'gem'})
        own_repo = p.own_repo()
        p2_own_repo = p2.own_repo()
        p.external_repos.add(p2_own_repo)

        self.assertTrue(own_repo)
        self.assertTrue(own_repo.base_url)
        self.assertFalse(own_repo.git_url)
        self.assertFalse(own_repo.url)
        self.assertEqual(own_repo.name(), 'unicore-cms-content-ffl-za')

        external_repo = p.external_repos.get()
        self.assertEqual(p2_own_repo, external_repo)
        self.assertEqual(external_repo.name(), 'unicore-cms-content-gem-uk')

        self.assertEqual(len(p.all_repos()), 2)
        own_repo.delete()
        p = Project.objects.get(pk=p.pk)
        self.assertIs(p.own_repo(), None)
        self.assertEqual(len(p.all_repos()), 1)

    def test_get_marathon_app_data(self):
        p = self.mk_project(app_type={
            'name': 'gem',
            'title': 'Girl Effect',
            'project_type': 'unicore-cms',
            'docker_image': 'universalcore/unicore-cms-gem'
        }, project={
            'marathon_health_check_path': '/health/'
        })

        self.assertEquals(p.get_marathon_app_data(), {
            "id": "gem-za-%s" % p.id,
            "cmd": (
                "/usr/local/bin/uwsgi "
                "--ini-paste /var/unicore-configs/"
                "frontend_settings/gem_za.ini "
                "--http :5656 "
                "--processes 1 "
                "--threads 1 "
                "--static-map /static=/var/app/static"
            ),
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "labels": {
                "domain": 'gem-za-%s.qa-hub.unicore.io' % p.id,
                "country": "South Africa",
                "project_type": "unicore-cms",
                "HAPROXY_GROUP": "external",
                "HAPROXY_0_VHOST": 'gem-za-%s.qa-hub.unicore.io' % p.id,
            },
            "container": {
                "type": "DOCKER",
                "docker": {
                    "image": "universalcore/unicore-cms-gem",
                    "forcePullImage": True,
                    "network": "BRIDGE",
                    "portMappings": [{"containerPort": 5656, "hostPort": 0}],
                    "parameters": [{
                        "key": "add-host",
                        "value": "servicehost:127.0.0.1"}]
                },
                "volumes": [{
                    "containerPath": "/var/unicore-configs",
                    "hostPath": "/path/to/unicore-configs",
                    "mode": "RO"
                }]
            },
            "ports": [0],
            "healthChecks": [{
                "gracePeriodSeconds": 3,
                "intervalSeconds": 10,
                "maxConsecutiveFailures": 3,
                "path": "/health/",
                "portIndex": 0,
                "protocol": "HTTP",
                "timeoutSeconds": 5
            }],
        })
        p = self.mk_project(
            app_type={
                'project_type': 'springboard',
                'docker_image': 'universalcore/springboard-ffl'},
            project={
                'country': 'TZ',
                'marathon_health_check_path': '/health/',
            })

        self.assertEquals(p.get_marathon_app_data(), {
            "id": "ffl-tz-%s" % p.id,
            "cmd": (
                "/usr/local/bin/uwsgi "
                "--ini-paste /var/unicore-configs/"
                "springboard_settings/ffl_tz.ini "
                "--http :5656 "
                "--processes 1 "
                "--threads 1 "
                "--static-map /static=/var/app/static"
            ),
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "labels": {
                "domain": u"ffl-tz-%s.qa-hub.unicore.io" % p.id,
                "country": u"Tanzania, United Republic of",
                "project_type": "springboard",
                "HAPROXY_GROUP": "external",
                "HAPROXY_0_VHOST": u"ffl-tz-%s.qa-hub.unicore.io" % p.id,
            },
            "container": {
                "type": "DOCKER",
                "docker": {
                    "image": "universalcore/springboard-ffl",
                    "forcePullImage": True,
                    "network": "BRIDGE",
                    "portMappings": [{"containerPort": 5656, "hostPort": 0}],
                    "parameters": [{
                        "key": "add-host",
                        "value": "servicehost:127.0.0.1"}]
                },
                "volumes": [{
                    "containerPath": "/var/unicore-configs",
                    "hostPath": "/path/to/unicore-configs",
                    "mode": "RO"
                }]
            },
            "ports": [0],
            "healthChecks": [{
                "gracePeriodSeconds": 3,
                "intervalSeconds": 10,
                "maxConsecutiveFailures": 3,
                "path": "/health/",
                "portIndex": 0,
                "protocol": "HTTP",
                "timeoutSeconds": 5
            }],
        })

        p = self.mk_project(project={'application_type': None})

        with self.assertRaises(exceptions.ProjectTypeRequiredException):
            p.get_marathon_app_data()
