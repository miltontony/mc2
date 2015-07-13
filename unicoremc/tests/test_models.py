import pytest

from django.contrib.auth.models import User

from mock import patch, Mock

from unicoremc.tests.base import UnicoremcTestCase
from unicoremc.models import Project, AppType, ProjectRepo, standalone_only
from unicoremc import exceptions


@pytest.mark.django_db
class ModelsTestCase(UnicoremcTestCase):
    fixtures = ['test_users.json', 'test_social_auth.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')

    def test_app_type_title(self):
        app_type = AppType._for('gem', 'Girl Effect', 'unicore-cms')
        self.assertEquals(str(app_type), 'Girl Effect (unicore-cms)')

    def test_project_app_type(self):
        app_type = AppType._for('gem', 'Girl Effect', 'unicore-cms')

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
        other_repo = ProjectRepo._for(p, p2_own_repo)

        self.assertTrue(own_repo)
        self.assertTrue(own_repo.base_url)
        self.assertFalse(own_repo.repo)
        self.assertFalse(own_repo.git_url)
        self.assertFalse(own_repo.url)
        self.assertEqual(own_repo.name(), 'unicore-cms-content-ffl-za')

        self.assertEqual(other_repo, p.repos.exclude(pk=own_repo.pk).get())
        other_repo = p.repos.exclude(pk=own_repo.pk).get()
        self.assertEqual(other_repo.repo, p2_own_repo)
        self.assertEqual(other_repo.project, p)
        self.assertEqual(other_repo.base_url, p2_own_repo.base_url)
        self.assertEqual(other_repo.url, p2_own_repo.url)
        self.assertEqual(other_repo.git_url, p2_own_repo.git_url)
        self.assertEqual(other_repo.name(), p2_own_repo.name())
        self.assertEqual(other_repo.name(), 'unicore-cms-content-gem-uk')
        self.assertNotEqual(other_repo, other_repo.repo)

        own_repo.delete()
        self.assertIs(p.own_repo(), None)
        self.assertEqual(p.repos.count(), 1)

    def test_standalone_only_decorator(self):
        class P(object):
            def __init__(self, own_repo):
                self._own_repo = own_repo
                self.called_test_method = False

            def own_repo(self):
                return self._own_repo

            @standalone_only
            def test_method(self):
                self.called_test_method = True
                return 'foo'

        p = P(own_repo=True)
        self.assertEqual(p.test_method(), 'foo')
        self.assertTrue(p.called_test_method)

        p = P(own_repo=False)
        self.assertIs(p.test_method(), None)
        self.assertFalse(p.called_test_method)

    def test_get_marathon_app_data(self):
        p = self.mk_project(app_type={
            'name': 'gem',
            'title': 'Girl Effect',
            'project_type': 'unicore-cms'})

        self.assertEquals(p.get_marathon_app_data(), {
            "id": "gem-za-%s" % p.id,
            "cmd":
                '/var/praekelt/python/bin/gunicorn --bind localhost:$PORT '
                '--paste /path/to/unicore-configs/frontend_settings/gem_za.ini'
                ' --preload',
            "cpus": 0.1,
            "mem": 100.0,
            "instances": 1,
            "labels": {
                "domain": 'za.gem.qa-hub.unicore.io ',
                "country": "South Africa",
                "project_type": "unicore-cms",
            },
        })
        p = self.mk_project(
            app_type={'project_type': 'springboard'},
            project={'country': 'TZ'})

        self.assertEquals(p.get_marathon_app_data(), {
            "id": "ffl-tz-%s" % p.id,
            "cmd":
                '/var/praekelt/springboard-python/bin/gunicorn --bind'
                ' localhost:$PORT --paste'
                ' /path/to/unicore-configs/springboard_settings/ffl_tz.ini'
                ' --preload',
            "cpus": 0.1,
            "mem": 100.0,
            "instances": 1,
            "labels": {
                "domain": 'tz.ffl.qa-hub.unicore.io ',
                "country": "Tanzania, United Republic of",
                "project_type": "springboard",
            },
        })

        p = self.mk_project(project={'application_type': None})

        with self.assertRaises(exceptions.ProjectTypeRequiredException):
            p.get_marathon_app_data()

        p = self.mk_project(
            app_type={'project_type': 'foo-bar'},
            project={'country': 'TZ'})

        with self.assertRaises(exceptions.ProjectTypeUnknownException):
            p.get_marathon_app_data()
