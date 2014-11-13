import os
import pytest
import responses
import shutil

from django.conf import settings

from unicoremc.models import Project
from unicoremc.states import ProjectWorkflow
from unicoremc.tests.base import UnicoremcTestCase


@pytest.mark.django_db
class StatesTestCase(UnicoremcTestCase):

    def setUp(self):
        self.mk_test_repos()

    def test_initial_state(self):
        p = Project(
            app_type='ffl',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='ZA',
            owner=self.user)
        p.save()
        self.assertEquals(p.state, 'initial')

    @responses.activate
    def test_finish_state(self):
        def create_db_call_mock(*call_args, **call_kwargs):
            cwd = call_kwargs.get('cwd')
            env = call_kwargs.get('env')
            [args] = call_args
            self.assertEqual(cwd, settings.UNICORE_CMS_INSTALL_DIR)
            self.assertEqual(
                env, {'DJANGO_SETTINGS_MODULE': 'project.ffl_za_settings'})
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
                env, {'DJANGO_SETTINGS_MODULE': 'project.ffl_za_settings'})
            self.assertTrue('/path/to/bin/python' in args)
            self.assertTrue(
                os.path.join(settings.UNICORE_CMS_INSTALL_DIR, 'manage.py')
                in args)
            self.assertTrue('import_from_git' in args)
            self.assertTrue('--quiet' in args)

        self.mock_create_repo()
        self.mock_create_webhook()

        p = Project(
            app_type='ffl',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='ZA',
            owner=self.user)
        p.save()

        self.addCleanup(lambda: shutil.rmtree(p.repo_path()))
        self.addCleanup(lambda: shutil.rmtree(p.frontend_repo_path()))

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo', access_token='sample-token')
        pw.take_action('clone_repo')
        pw.take_action('create_remote')
        pw.take_action('merge_remote')
        pw.take_action('push_repo')
        pw.take_action('create_webhook', access_token='sample-token')
        pw.take_action('init_workspace')
        pw.take_action('create_supervisor')
        pw.take_action('create_nginx')
        pw.take_action('create_pyramid_settings')
        pw.take_action('create_cms_settings')

        p.db_manager.call_subprocess = create_db_call_mock
        pw.take_action('create_db')

        p.db_manager.call_subprocess = init_db_call_mock
        pw.take_action('init_db')

        pw.take_action('finish')

        self.assertEquals(p.state, 'done')

    @responses.activate
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

    @responses.activate
    def test_automation_using_next(self):

        def call_mock(*call_args, **call_kwargs):
            pass

        self.mock_create_repo()
        self.mock_create_webhook()

        p = Project(
            app_type='ffl',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='ZA',
            owner=self.user)
        p.save()

        p.db_manager.call_subprocess = call_mock

        self.addCleanup(lambda: shutil.rmtree(p.repo_path()))
        self.addCleanup(lambda: shutil.rmtree(p.frontend_repo_path()))

        self.assertEquals(p.state, 'initial')

        pw = ProjectWorkflow(instance=p)
        pw.run_all(access_token='sample-token')

        self.assertEquals(p.state, 'done')
        self.assertEquals(
            p.repo_url,
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

        self.mock_create_repo()
        self.mock_create_webhook()

        p = Project(
            app_type='ffl',
            base_repo_url=self.base_repo_sm.repo.git_dir,
            country='ZA',
            owner=self.user)
        p.save()

        p.db_manager.call_subprocess = call_mock

        self.assertEquals(p.state, 'initial')

        pw = ProjectWorkflow(instance=p)
        pw.run_all(access_token='sample-token')

        self.assertEquals(p.state, 'done')
        pw.take_action('destroy')

        frontend_settings_path = os.path.join(
            settings.FRONTEND_SETTINGS_OUTPUT_PATH,
            'ffl.production.za.ini')

        cms_settings_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za_settings.py')

        frontend_supervisor_config_path = os.path.join(
            settings.SUPERVISOR_CONFIGS_PATH,
            'frontend_ffl_za.conf')

        cms_supervisor_config_path = os.path.join(
            settings.SUPERVISOR_CONFIGS_PATH,
            'cms_ffl_za.conf')

        frontend_nginx_config_path = os.path.join(
            settings.NGINX_CONFIGS_PATH,
            'frontend_ffl_za.conf')

        cms_nginx_config_path = os.path.join(
            settings.NGINX_CONFIGS_PATH,
            'cms_ffl_za.conf')

        self.assertFalse(os.path.exists(frontend_supervisor_config_path))
        self.assertFalse(os.path.exists(cms_supervisor_config_path))
        self.assertFalse(os.path.exists(frontend_nginx_config_path))
        self.assertFalse(os.path.exists(cms_nginx_config_path))

        self.assertFalse(os.path.exists(p.repo_path()))
        self.assertFalse(os.path.exists(p.frontend_repo_path()))

        self.assertFalse(os.path.exists(frontend_settings_path))
        self.assertFalse(os.path.exists(cms_settings_path))

        self.assertFalse(os.path.exists(cms_db_path))
