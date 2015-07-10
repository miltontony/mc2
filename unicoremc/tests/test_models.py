import pytest

from django.contrib.auth.models import User

from unicoremc.tests.base import UnicoremcTestCase
from unicoremc.models import Project, AppType
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
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

        self.assertEquals(p.app_type, '')

        p = Project(
            application_type=app_type,
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

        self.assertEquals(p.app_type, 'gem')

    def test_get_marathon_app_data(self):
        gem = AppType._for('gem', 'Girl Effect', 'unicore-cms')
        ffl = AppType._for('ffl', 'Facts for Life', 'springboard')
        p = Project(
            application_type=gem,
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

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
                "project_type": "unicore-cms",
            },
        })
        p = Project(
            application_type=ffl,
            base_repo_url='http://some-git-repo.com',
            country='TZ',
            owner=self.user)
        p.save()

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
                "project_type": "springboard",
            },
        })

        p = Project(
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

        with self.assertRaises(exceptions.ProjectTypeRequiredException):
            p.get_marathon_app_data()

        ffl_unknown = AppType._for('ffl', 'Facts for Life', 'foo-bar')
        p = Project(
            application_type=ffl_unknown,
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

        with self.assertRaises(exceptions.ProjectTypeUnknownException):
            p.get_marathon_app_data()
