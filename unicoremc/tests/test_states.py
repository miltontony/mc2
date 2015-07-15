import os
import pytest
import responses
import shutil

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from mock import patch

from unicoremc.models import Project, publish_to_websocket
from unicoremc.states import ProjectWorkflow
from unicoremc.tests.base import UnicoremcTestCase


@pytest.mark.django_db
class StatesTestCase(UnicoremcTestCase):
    fixtures = ['test_users.json', 'test_social_auth.json']

    def setUp(self):
        self.mk_test_repos()
        self.user = User.objects.get(username='testuser')
        post_save.disconnect(publish_to_websocket, sender=Project)

    def test_initial_state(self):
        p = self.mk_project(repo={'base_url': self.base_repo_sm.repo.git_dir})
        self.assertEquals(p.state, 'initial')

    @responses.activate
    def test_finish_state(self):
        def create_db_call_mock(*call_args, **call_kwargs):
            cwd = call_kwargs.get('cwd')
            env = call_kwargs.get('env')
            [args] = call_args
            self.assertEqual(cwd, settings.UNICORE_CMS_INSTALL_DIR)
            self.assertEqual(
                env, {'DJANGO_SETTINGS_MODULE': 'project.ffl_za'})
            self.assertTrue('/path/to/bin/python' in args)
            self.assertTrue(
                os.path.join(settings.UNICORE_CMS_INSTALL_DIR, 'manage.py')
                in args)
            self.assertTrue('syncdb' in args)
            self.assertTrue('--migrate' in args)
            self.assertTrue('--noinput' in args)

        def init_db_call_mock(*call_args, **call_kwargs):
            cwd = call_kwargs.get('cwd')
            env = call_kwargs.get('env')
            [args] = call_args

            self.assertEqual(cwd, settings.UNICORE_CMS_INSTALL_DIR)
            self.assertEqual(
                env, {'DJANGO_SETTINGS_MODULE': 'project.ffl_za'})
            self.assertTrue('/path/to/bin/python' in args)
            self.assertTrue(
                os.path.join(settings.UNICORE_CMS_INSTALL_DIR, 'manage.py')
                in args)
            self.assertTrue('import_from_git' in args)
            self.assertTrue('--quiet' in args)

        self.mock_create_all()

        p = self.mk_project(repo={'base_url': self.base_repo_sm.repo.git_dir})

        self.addCleanup(lambda: shutil.rmtree(p.repo_path()))

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo', access_token='sample-token')
        pw.take_action('clone_repo')
        pw.take_action('create_remote')
        pw.take_action('merge_remote')
        pw.take_action('push_repo')
        pw.take_action('create_webhook', access_token='sample-token')
        pw.take_action('init_workspace')
        pw.take_action('create_nginx')
        pw.take_action('create_hub_app')
        pw.take_action('create_pyramid_settings')
        pw.take_action('create_cms_settings')

        p.db_manager.call_subprocess = create_db_call_mock
        pw.take_action('create_db')

        p.db_manager.call_subprocess = init_db_call_mock
        pw.take_action('init_db')
        pw.take_action('create_marathon_app')

        pw.take_action('finish')

        self.assertEquals(p.state, 'done')

    @responses.activate
    def test_next(self):
        self.mock_create_repo()
        p = self.mk_project(repo={'base_url': self.base_repo_sm.repo.git_dir})

        self.assertEquals(p.state, 'initial')

        pw = ProjectWorkflow(instance=p)
        pw.next(access_token='sample-token')
        self.assertEquals(p.state, 'repo_created')

    @responses.activate
    def test_automation_using_next(self):

        def call_mock(*call_args, **call_kwargs):
            pass

        self.mock_create_all()

        p = self.mk_project(repo={'base_url': self.base_repo_sm.repo.git_dir})

        p.db_manager.call_subprocess = call_mock

        self.addCleanup(lambda: shutil.rmtree(p.repo_path()))

        self.assertEquals(p.state, 'initial')

        pw = ProjectWorkflow(instance=p)
        pw.run_all(access_token='sample-token')

        self.assertEquals(p.state, 'done')
        self.assertEquals(
            p.own_repo().url,
            self.source_repo_sm.repo.git_dir)

    @responses.activate
    def test_destroy(self):
        cms_db_path = os.path.join(
            settings.UNICORE_CMS_INSTALL_DIR,
            'django_cms_ffl_za.db')

        def call_mock(*call_args, **call_kwargs):
            if not os.path.exists(settings.UNICORE_CMS_INSTALL_DIR):
                os.makedirs(settings.UNICORE_CMS_INSTALL_DIR)

            with open(cms_db_path, 'a'):
                os.utime(cms_db_path, None)

        self.mock_create_all()

        p = self.mk_project(repo={'base_url': self.base_repo_sm.repo.git_dir})

        p.db_manager.call_subprocess = call_mock

        self.assertEquals(p.state, 'initial')

        pw = ProjectWorkflow(instance=p)
        pw.run_all(access_token='sample-token')

        self.assertEquals(p.state, 'done')

        frontend_settings_path = os.path.join(
            settings.FRONTEND_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')

        cms_settings_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.py')

        cms_uwsgi_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')

        cms_nginx_config_path = os.path.join(
            settings.NGINX_CONFIGS_PATH,
            'cms_ffl_za.conf')

        self.assertTrue(os.path.exists(cms_nginx_config_path))

        self.assertTrue(os.path.exists(p.repo_path()))
        self.assertFalse(os.path.exists(p.frontend_repo_path()))

        self.assertTrue(os.path.exists(frontend_settings_path))
        self.assertTrue(os.path.exists(cms_settings_path))
        self.assertTrue(os.path.exists(cms_uwsgi_path))

        self.assertTrue(os.path.exists(cms_db_path))

        pw.take_action('destroy')

        self.assertFalse(os.path.exists(cms_nginx_config_path))

        self.assertFalse(os.path.exists(p.repo_path()))
        self.assertFalse(os.path.exists(p.frontend_repo_path()))

        self.assertFalse(os.path.exists(frontend_settings_path))
        self.assertFalse(os.path.exists(cms_settings_path))
        self.assertFalse(os.path.exists(cms_uwsgi_path))

        self.assertFalse(os.path.exists(cms_db_path))

    @responses.activate
    def test_destroy_springboard(self):
        cms_db_path = os.path.join(
            settings.UNICORE_CMS_INSTALL_DIR,
            'django_cms_ffl_za.db')

        def call_mock(*call_args, **call_kwargs):
            if not os.path.exists(settings.UNICORE_CMS_INSTALL_DIR):
                os.makedirs(settings.UNICORE_CMS_INSTALL_DIR)

            with open(cms_db_path, 'a'):
                os.utime(cms_db_path, None)

        self.mock_create_all()

        p = self.mk_project(
            repo={'base_url': self.base_repo_sm.repo.git_dir},
            app_type={'project_type': 'springboard'})

        p.db_manager.call_subprocess = call_mock

        self.assertEquals(p.state, 'initial')

        pw = ProjectWorkflow(instance=p)
        pw.run_all(access_token='sample-token')

        self.assertEquals(p.state, 'done')

        frontend_settings_path = os.path.join(
            settings.SPRINGBOARD_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')

        cms_settings_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.py')

        cms_uwsgi_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')

        cms_nginx_config_path = os.path.join(
            settings.NGINX_CONFIGS_PATH,
            'cms_ffl_za.conf')

        self.assertTrue(os.path.exists(cms_nginx_config_path))

        self.assertTrue(os.path.exists(p.repo_path()))
        self.assertFalse(os.path.exists(p.frontend_repo_path()))

        self.assertTrue(os.path.exists(frontend_settings_path))
        self.assertTrue(os.path.exists(cms_settings_path))
        self.assertTrue(os.path.exists(cms_uwsgi_path))

        self.assertTrue(os.path.exists(cms_db_path))

        pw.take_action('destroy')

        self.assertFalse(os.path.exists(cms_nginx_config_path))

        self.assertFalse(os.path.exists(p.repo_path()))

        self.assertFalse(os.path.exists(frontend_settings_path))
        self.assertFalse(os.path.exists(cms_settings_path))
        self.assertFalse(os.path.exists(cms_uwsgi_path))

        self.assertFalse(os.path.exists(cms_db_path))

    @responses.activate
    def test_full_run_with_unicode(self):
        cms_db_path = os.path.join(
            settings.UNICORE_CMS_INSTALL_DIR,
            'django_cms_ffl_za.db')

        def call_mock(*call_args, **call_kwargs):
            if not os.path.exists(settings.UNICORE_CMS_INSTALL_DIR):
                os.makedirs(settings.UNICORE_CMS_INSTALL_DIR)

            with open(cms_db_path, 'a'):
                os.utime(cms_db_path, None)

        self.mock_create_all()

        p = self.mk_project(repo={'base_url': self.base_repo_sm.repo.git_dir})

        p.db_manager.call_subprocess = call_mock

        self.assertEquals(p.state, 'initial')

        pw = ProjectWorkflow(instance=p)
        pw.run_all(access_token='sample-token')

        self.assertEquals(p.state, 'done')

        frontend_settings_path = os.path.join(
            settings.FRONTEND_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')

        cms_settings_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.py')

        cms_uwsgi_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')

        cms_nginx_config_path = os.path.join(
            settings.NGINX_CONFIGS_PATH,
            'cms_ffl_za.conf')

        self.assertTrue(os.path.exists(cms_nginx_config_path))

        self.assertTrue(os.path.exists(p.repo_path()))
        self.assertFalse(os.path.exists(p.frontend_repo_path()))

        self.assertTrue(os.path.exists(frontend_settings_path))
        self.assertTrue(os.path.exists(cms_settings_path))
        self.assertTrue(os.path.exists(cms_uwsgi_path))

        self.assertTrue(os.path.exists(cms_db_path))

        pw.take_action('destroy')

        self.assertFalse(os.path.exists(cms_nginx_config_path))

        self.assertFalse(os.path.exists(p.repo_path()))
        self.assertFalse(os.path.exists(p.frontend_repo_path()))

        self.assertFalse(os.path.exists(frontend_settings_path))
        self.assertFalse(os.path.exists(cms_settings_path))
        self.assertFalse(os.path.exists(cms_uwsgi_path))

        self.assertFalse(os.path.exists(cms_db_path))

    @patch('unicoremc.managers.database.DbManager.call_subprocess')
    @responses.activate
    def test_non_standalone_project_workflow(self, mock_subprocess):
        existing_repo = self.mk_project().own_repo()
        p = self.mk_project()
        p.own_repo().delete()
        p.external_repos.add(existing_repo)
        p = Project.objects.get(pk=p.pk)
        self.assertIs(p.own_repo(), None)

        self.mock_create_all()

        pw = ProjectWorkflow(instance=p)
        pw.run_all(access_token='sample-token')

        frontend_settings_path = os.path.join(
            settings.FRONTEND_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')
        cms_settings_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.py')
        cms_uwsgi_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')
        cms_nginx_config_path = os.path.join(
            settings.NGINX_CONFIGS_PATH,
            'cms_ffl_za.conf')
        cms_db_path = os.path.join(
            settings.UNICORE_CMS_INSTALL_DIR,
            'django_cms_ffl_za.db')

        # check that frontend pyramid and nginx configs were created
        self.assertTrue(os.path.exists(frontend_settings_path))
        # check that unicore.hub and marathon were set up for frontend
        self.assertTrue(p.hub_app_id)
        self.assertEqual(len(filter(
            lambda c: settings.MESOS_MARATHON_HOST in c.request.url,
            responses.calls)), 1)

        # check that repos and CMS configs were not created
        self.assertFalse(os.path.exists(cms_nginx_config_path))
        self.assertFalse(os.path.exists(p.repo_path()))
        self.assertFalse(os.path.exists(p.frontend_repo_path()))
        self.assertFalse(os.path.exists(cms_settings_path))
        self.assertFalse(os.path.exists(cms_uwsgi_path))
        self.assertFalse(os.path.exists(cms_db_path))
        self.assertFalse(filter(
            lambda c: settings.GITHUB_HOOKS_API in c.request.url,
            responses.calls))
        self.assertFalse(filter(
            lambda c: settings.UNICORE_DISTRIBUTE_HOST in c.request.url,
            responses.calls))

        pw.take_action('destroy')
        self.assertFalse(os.path.exists(frontend_settings_path))
