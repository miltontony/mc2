import json
import httpretty
import os
import shutil

from git import Repo
from elasticgit.manager import StorageManager

from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings

from unicoremc.models import Project
from unicoremc.states import ProjectWorkflow


@httpretty.activate
class StatesTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='testuser',
            email="test@email.com")

        workdir = os.path.join(settings.CMS_REPO_PATH, 'test-source-repo')

        # NOTE: StorageManager.create_storage() should take a repo path
        # and should be a class method
        if not os.path.exists(workdir):
            os.makedirs(workdir)

        self.source_repo_sm = StorageManager(Repo.init(workdir))
        self.source_repo_sm.create_storage()
        self.source_repo_sm.write_config('user', {
            'name': 'testuser',
            'email': 'test@email.com',
        })

        workdir = os.path.join(settings.CMS_REPO_PATH, 'test-base-repo')
        if not os.path.exists(workdir):
            os.makedirs(workdir)

        self.base_repo_sm = StorageManager(Repo.init(workdir))
        self.base_repo_sm.create_storage()
        self.base_repo_sm.write_config('user', {
            'name': 'testuser',
            'email': 'test@email.com',
        })

        try:
            # TODO: Use `pw.take_action('destory')` to cleanup
            shutil.rmtree(os.path.join(settings.CMS_REPO_PATH, 'ffl-za'))
        except:
            pass

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()
        self.source_repo_sm.destroy_storage()
        self.base_repo_sm.destroy_storage()

        try:
            # TODO: Use `pw.take_action('destory')` to cleanup
            shutil.rmtree(os.path.join(settings.CMS_REPO_PATH, 'ffl-za'))
        except:
            pass

    def mock_create_repo(self):
        httpretty.register_uri(
            httpretty.POST,
            settings.GITHUB_API + 'repos',
            body=json.dumps({
                'clone_url': self.source_repo_sm.repo.git_dir,
            }),
            status=201,
            content_type="application/json")

    def test_initial_state(self):
        p = Project(
            app_type='ffl',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='ZA',
            owner=self.user)
        p.save()
        self.assertEquals(p.state, 'initial')

    def test_create_repo_state(self):
        self.mock_create_repo()

        p = Project(
            app_type='ffl',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='ZA',
            owner=self.user)
        p.save()
        self.assertEquals(p.state, 'initial')

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo', access_token='sample-token')

        self.assertEquals(
            p.repo_url,
            self.source_repo_sm.repo.git_dir)
        self.assertEquals(p.state, 'repo_created')

    def test_clone_repo_state(self):
        self.mock_create_repo()
        p = Project(
            app_type='ffl',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='ZA',
            owner=self.user)
        p.save()

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo', access_token='sample-token')
        pw.take_action('clone_repo')

        self.assertEquals(p.state, 'repo_cloned')

    def test_create_remote_state(self):
        self.mock_create_repo()
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

    def test_supervisor_create_state(self):
        self.mock_create_repo()
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
        pw.take_action('create_supervisor')

        self.assertEquals(p.state, 'supervisor_created')

    def test_nginx_create_state(self):
        self.mock_create_repo()
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
        pw.take_action('create_supervisor')
        pw.take_action('create_nginx')

        self.assertEquals(p.state, 'nginx_created')

    def test_pyramid_settings_created_state(self):
        self.mock_create_repo()
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
        pw.take_action('create_supervisor')
        pw.take_action('create_nginx')
        pw.take_action('create_pyramid_settings')

        self.assertEquals(p.state, 'pyramid_settings_created')

    def test_cms_settings_create_state(self):
        self.mock_create_repo()
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
        pw.take_action('create_supervisor')
        pw.take_action('create_nginx')
        pw.take_action('create_pyramid_settings')
        pw.take_action('create_cms_settings')

        self.assertEquals(p.state, 'cms_settings_created')

    def test_db_create_state(self):
        self.mock_create_repo()
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
        pw.take_action('create_supervisor')
        pw.take_action('create_nginx')
        pw.take_action('create_pyramid_settings')
        pw.take_action('create_cms_settings')
        pw.take_action('create_db')

        self.assertEquals(p.state, 'db_created')

    def test_db_init_state(self):
        self.mock_create_repo()
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
        pw.take_action('create_supervisor')
        pw.take_action('create_nginx')
        pw.take_action('create_pyramid_settings')
        pw.take_action('create_cms_settings')
        pw.take_action('create_db')
        pw.take_action('init_db')

        self.assertEquals(p.state, 'db_initialized')

    def test_cms_init_state(self):
        self.mock_create_repo()
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
        pw.take_action('create_supervisor')
        pw.take_action('create_nginx')
        pw.take_action('create_pyramid_settings')
        pw.take_action('create_cms_settings')
        pw.take_action('create_db')
        pw.take_action('init_db')
        pw.take_action('init_cms')

        self.assertEquals(p.state, 'cms_initialized')

    def test_supervisor_reload_state(self):
        self.mock_create_repo()
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
        pw.take_action('create_supervisor')
        pw.take_action('create_nginx')
        pw.take_action('create_pyramid_settings')
        pw.take_action('create_cms_settings')
        pw.take_action('create_db')
        pw.take_action('init_db')
        pw.take_action('init_cms')
        pw.take_action('reload_supervisor')

        self.assertEquals(p.state, 'supervisor_reloaded')

    def test_nginx_reload_state(self):
        self.mock_create_repo()
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
        pw.take_action('create_supervisor')
        pw.take_action('create_nginx')
        pw.take_action('create_pyramid_settings')
        pw.take_action('create_cms_settings')
        pw.take_action('create_db')
        pw.take_action('init_db')
        pw.take_action('init_cms')
        pw.take_action('reload_supervisor')
        pw.take_action('reload_nginx')

        self.assertEquals(p.state, 'nginx_reloaded')

    def test_finish_state(self):
        self.mock_create_repo()
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
        pw.take_action('create_supervisor')
        pw.take_action('create_nginx')
        pw.take_action('create_pyramid_settings')
        pw.take_action('create_cms_settings')
        pw.take_action('create_db')
        pw.take_action('init_db')
        pw.take_action('init_cms')
        pw.take_action('reload_supervisor')
        pw.take_action('reload_nginx')
        pw.take_action('finish')

        self.assertEquals(p.state, 'done')

    def test_next(self):
        self.mock_create_repo()
        p = Project(
            app_type='ffl',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='ZA',
            owner=self.user)
        p.save()
        self.assertEquals(p.state, 'initial')

        pw = ProjectWorkflow(instance=p)
        pw.next(access_token='sample-token')
        self.assertEquals(p.state, 'repo_created')

    def test_automation_using_next(self):
        self.mock_create_repo()
        p = Project(
            app_type='ffl',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='ZA',
            owner=self.user)
        p.save()
        self.assertEquals(p.state, 'initial')

        pw = ProjectWorkflow(instance=p)
        pw.run_all(access_token='sample-token')

        self.assertEquals(p.state, 'done')
        self.assertEquals(
            p.repo_url,
            self.source_repo_sm.repo.git_dir)
