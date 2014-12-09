import responses
import pytest
import os
import shutil

from unittest import skip

from django.conf import settings
from django.contrib.auth.models import User

from git import Repo

from unicoremc.models import Project, Localisation
from unicoremc.states import ProjectWorkflow
from unicoremc import exceptions
from unicoremc.tests.base import UnicoremcTestCase

from unicore.content.models import (
    Category, Page, Localisation as EGLocalisation)


@pytest.mark.django_db
class ProjectTestCase(UnicoremcTestCase):
    fixtures = ['test_users.json', 'test_social_auth.json']

    def setUp(self):
        self.mk_test_repos()
        self.user = User.objects.get(username='testuser')

    @responses.activate
    def test_create_repo_state(self):
        self.mock_create_repo()
        self.mock_create_webhook()

        p = Project(
            app_type='ffl',
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo', access_token='sample-token')

        self.assertEquals(
            p.repo_url,
            self.source_repo_sm.repo.git_dir)
        self.assertEquals(p.state, 'repo_created')

    @responses.activate
    def test_create_repo_missing_access_token(self):
        self.mock_create_repo()
        self.mock_create_webhook()

        p = Project(
            app_type='ffl',
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

        with self.assertRaises(exceptions.AccessTokenRequiredException):
            pw = ProjectWorkflow(instance=p)
            pw.take_action('create_repo')

        self.assertEquals(p.state, 'initial')

    @responses.activate
    def test_create_repo_bad_response(self):
        self.mock_create_repo(status=404, data={'message': 'Not authorized'})

        p = Project(
            app_type='ffl',
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

        with self.assertRaises(exceptions.GithubApiException):
            pw = ProjectWorkflow(instance=p)
            pw.take_action('create_repo', access_token='sample-token')

        self.assertEquals(p.state, 'initial')

    @responses.activate
    def test_clone_repo(self):
        self.mock_create_repo()
        self.mock_create_webhook()

        p = Project(
            app_type='ffl',
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo', access_token='sample-token')
        pw.take_action('clone_repo')

        self.assertEquals(p.state, 'repo_cloned')
        self.assertTrue(os.path.isdir(os.path.join(p.repo_path(), '.git')))
        self.assertFalse(
            os.path.exists(os.path.join(p.repo_path(), 'README.md')))
        self.assertTrue(
            os.path.exists(os.path.join(p.repo_path(), 'text.txt')))

        self.addCleanup(lambda: shutil.rmtree(p.repo_path()))

    @responses.activate
    def test_create_remotes_repo(self):
        self.mock_create_repo()
        self.mock_create_webhook()

        p = Project(
            app_type='ffl',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='ZA',
            owner=self.user)
        p.save()

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo', access_token='sample-token')
        pw.take_action('clone_repo')
        pw.take_action('create_remote')

        self.assertEquals(p.state, 'remote_created')
        self.assertTrue(os.path.isdir(os.path.join(p.repo_path(), '.git')))

        repo = Repo(p.repo_path())
        self.assertEquals(len(repo.remotes), 2)
        self.assertEquals(
            repo.remote(name='upstream').url,
            self.base_repo_sm.repo.git_dir)

        self.addCleanup(lambda: shutil.rmtree(p.repo_path()))

    @skip("slow test that connects to github")
    def test_create_remotes_repo_from_github(self):
        self.mock_create_repo()
        self.mock_create_webhook()

        p = Project(
            app_type='ffl',
            base_repo_url=(
                'git://github.com/universalcore/'
                'unicore-cms-content-gem-tanzania.git'),
            country='ZA',
            owner=self.user)
        p.save()

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo', access_token='sample-token')
        pw.take_action('clone_repo')
        pw.take_action('create_remote')
        pw.take_action('merge_remote')

        self.assertEquals(p.state, 'remote_merged')
        self.assertTrue(os.path.isdir(os.path.join(p.repo_path(), '.git')))
        self.assertTrue(
            os.path.exists(os.path.join(p.repo_path(), 'README.md')))

        repo = Repo(p.repo_path())
        self.assertEquals(len(repo.remotes), 2)
        self.assertEquals(
            repo.remote(name='upstream').url,
            ('git://github.com/universalcore/'
             'unicore-cms-content-gem-tanzania.git'))

        self.addCleanup(lambda: shutil.rmtree(p.repo_path()))

    @responses.activate
    def test_merge_remote_repo(self):
        self.mock_create_repo()
        self.mock_create_webhook()

        p = Project(
            app_type='ffl',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='ZA',
            owner=self.user)
        p.save()

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo', access_token='sample-token')
        pw.take_action('clone_repo')
        pw.take_action('create_remote')
        pw.take_action('merge_remote')

        self.assertEquals(p.state, 'remote_merged')
        self.assertTrue(os.path.isdir(os.path.join(p.repo_path(), '.git')))
        self.assertTrue(
            os.path.exists(os.path.join(p.repo_path(), 'sample.txt')))

        repo = Repo(p.repo_path())

        workspace = self.mk_workspace(
            working_dir=settings.CMS_REPO_PATH,
            name='ffl-za',
            index_prefix='unicore_cms_ffl_za')

        self.assertEqual(workspace.S(Category).count(), 1)
        self.assertEqual(workspace.S(Page).count(), 1)
        self.assertEqual(workspace.S(EGLocalisation).count(), 1)

        self.assertEquals(len(repo.remotes), 2)
        self.assertEquals(
            repo.remote(name='upstream').url,
            self.base_repo_sm.repo.git_dir)

        self.addCleanup(lambda: shutil.rmtree(p.repo_path()))

    @responses.activate
    def test_push_repo(self):
        self.mock_create_repo()
        self.mock_create_webhook()

        p = Project(
            app_type='ffl',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='ZA',
            owner=self.user)
        p.save()

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo', access_token='sample-token')
        pw.take_action('clone_repo')
        pw.take_action('create_remote')
        pw.take_action('merge_remote')

        self.assertFalse(os.path.exists(os.path.join(
            self.base_repo_sm.repo.working_dir, 'text.txt')))

        pw.take_action('push_repo')
        self.assertEquals(p.state, 'repo_pushed')

        self.assertTrue(os.path.exists(os.path.join(
            self.source_repo_sm.repo.working_dir, 'text.txt')))

        self.addCleanup(lambda: shutil.rmtree(p.repo_path()))

    @responses.activate
    def test_init_workspace(self):
        self.mock_create_repo()
        self.mock_create_webhook()

        p = Project(
            app_type='ffl',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='ZA',
            owner=self.user)
        p.save()

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo', access_token='sample-token')
        pw.take_action('clone_repo')
        pw.take_action('create_remote')
        pw.take_action('merge_remote')
        pw.take_action('push_repo')
        pw.take_action('create_webhook', access_token='sample-token')
        pw.take_action('init_workspace')

        self.assertEquals(p.state, 'workspace_initialized')

        workspace = self.mk_workspace(
            working_dir=settings.CMS_REPO_PATH,
            name='ffl-za',
            index_prefix='unicore_cms_ffl_za')

        self.assertEqual(workspace.S(Category).count(), 1)
        self.assertEqual(workspace.S(Page).count(), 1)
        self.assertEqual(workspace.S(EGLocalisation).count(), 1)

        cat = Category({
            'title': 'Some title',
            'slug': 'some-slug'
        })
        workspace.save(cat, 'Saving a Category')

        page = Page({
            'title': 'Some page title',
            'slug': 'some-page-slug'
        })
        workspace.save(page, 'Saving a Page')

        loc = EGLocalisation({
            'locale': 'spa_ES',
            'image': 'some-image-uuid',
            'image_host': 'http://some.site.com',
        })
        workspace.save(loc, 'Saving a Localisation')

        workspace.refresh_index()

        self.assertEqual(workspace.S(Category).count(), 2)
        self.assertEqual(workspace.S(Page).count(), 2)
        self.assertEqual(workspace.S(EGLocalisation).count(), 2)

        self.addCleanup(lambda: shutil.rmtree(p.repo_path()))
        self.addCleanup(lambda: shutil.rmtree(p.frontend_repo_path()))

    @responses.activate
    def test_create_nginx_config(self):
        self.mock_create_repo()
        self.mock_create_webhook()

        p = Project(
            app_type='ffl',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='ZA',
            owner=self.user)
        p.save()

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo', access_token='sample-token')
        pw.take_action('clone_repo')
        pw.take_action('create_remote')
        pw.take_action('merge_remote')
        pw.take_action('push_repo')
        pw.take_action('create_webhook', access_token='sample-token')
        pw.take_action('init_workspace')
        pw.take_action('create_nginx')

        frontend_nginx_config_path = os.path.join(
            settings.NGINX_CONFIGS_PATH,
            'frontend_ffl_za.conf')
        cms_nginx_config_path = os.path.join(
            settings.NGINX_CONFIGS_PATH,
            'cms_ffl_za.conf')

        self.assertTrue(os.path.exists(frontend_nginx_config_path))
        self.assertTrue(os.path.exists(cms_nginx_config_path))

        with open(frontend_nginx_config_path, "r") as config_file:
            data = config_file.read()

        self.assertTrue('za.ffl.qa-hub.unicore.io' in data)
        self.assertTrue('unicore_frontend_ffl_za-access.log' in data)
        self.assertTrue('unicore_frontend_ffl_za-error.log' in data)
        self.assertTrue(
            '/var/praekelt/unicore-cms-ffl/unicorecmsffl/static/' in data)

        with open(cms_nginx_config_path, "r") as config_file:
            data = config_file.read()

        self.assertTrue('cms.za.ffl.qa-hub.unicore.io' in data)
        self.assertTrue('unicore_cms_django_ffl_za-access.log' in data)
        self.assertTrue('unicore_cms_django_ffl_za-error.log' in data)

        self.addCleanup(lambda: shutil.rmtree(p.repo_path()))
        self.addCleanup(lambda: shutil.rmtree(p.frontend_repo_path()))

    @responses.activate
    def test_create_pyramid_settings(self):
        self.mock_create_repo()
        self.mock_create_webhook()

        p = Project(
            app_type='ffl',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='ZA',
            owner=self.user)
        p.save()
        p.available_languages.add(*[Localisation._for('eng_UK')])
        p.save()

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo', access_token='sample-token')
        pw.take_action('clone_repo')
        pw.take_action('create_remote')
        pw.take_action('merge_remote')
        pw.take_action('push_repo')
        pw.take_action('create_webhook', access_token='sample-token')
        pw.take_action('init_workspace')
        pw.take_action('create_nginx')
        pw.take_action('create_pyramid_settings')

        frontend_settings_path = os.path.join(
            settings.FRONTEND_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')

        self.assertTrue(os.path.exists(frontend_settings_path))

        with open(frontend_settings_path, "r") as config_file:
            data = config_file.read()

        self.assertTrue('egg:unicore-cms-ffl' in data)
        self.assertTrue(
            "[(u'eng_UK', u'English')]" in data)
        self.assertTrue(self.source_repo_sm.repo.working_dir in data)
        self.assertTrue(self.source_repo_sm.repo.git_dir in data)

        self.addCleanup(lambda: shutil.rmtree(p.repo_path()))
        self.addCleanup(lambda: shutil.rmtree(p.frontend_repo_path()))

    def test_ordering(self):
        p1 = Project.objects.create(
            app_type='ffl',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='ZA',
            owner=self.user)
        p2 = Project.objects.create(
            app_type='gem',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='KE',
            owner=self.user)
        p3 = Project.objects.create(
            app_type='ffl',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='KE',
            owner=self.user)

        self.assertEquals(Project.objects.all()[0], p3)
        self.assertEquals(Project.objects.all()[1], p1)
        self.assertEquals(Project.objects.all()[2], p2)
