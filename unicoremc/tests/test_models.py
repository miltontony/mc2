import pytest

from django.contrib.auth.models import User

from unicoremc.tests.base import UnicoremcTestCase
from unicoremc.models import Project, AppType, ProjectRepo
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

    def test_get_repo_attributes(self):
        app_type = AppType._for('gem', 'Girl Effect', 'unicore-cms')
        project = Project.objects.create(
            application_type=app_type,
            country='ZA',
            owner=self.user)
        repo = ProjectRepo.objects.create(
            project=project,
            base_url='http://some-git-repo.com',
            url='http://some-git-repo-clone.com',
            git_url='git://some-git-repo-clone.com')
        repo2 = ProjectRepo.objects.create(
            project=project,
            base_url='http://some-git-repo2.com',
            url='http://some-git-repo2-clone.com',
            git_url='git://some-git-repo2-clone.com')

        self.assertEqual(project.base_repo_urls(),
                         [repo.base_url, repo2.base_url])
        self.assertEqual(project.repo_urls(),
                         [repo.url, repo2.url])
        self.assertEqual(project.repo_git_urls(),
                         [repo.git_url, repo2.git_url])

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
