import os
import shutil

from django.conf import settings
from django.test.utils import override_settings

from unicoremc.tests.base import UnicoremcTestCase


class NginxManagerTestCase(UnicoremcTestCase):

    def test_write_frontend_nginx_configs(self):
        nm = self.get_nginx_manager()

        nm.write_frontend_nginx('ffl', 'za', 'some.domain.com')

        frontend_nginx_config_path = os.path.join(
            settings.NGINX_CONFIGS_PATH,
            'frontend_ffl_za.conf')

        frontend_socket_path = os.path.join(
            settings.FRONTEND_SOCKETS_PATH,
            'ffl_za.socket')

        self.assertTrue(os.path.exists(frontend_nginx_config_path))

        with open(frontend_nginx_config_path, "r") as config_file:
            data = config_file.read()

        self.addCleanup(lambda: os.remove(frontend_nginx_config_path))

        self.assertTrue(
            'server_name za.ffl.qa-hub.unicore.io some.domain.com' in data)
        self.assertTrue('za.ffl.qa-hub.unicore.io' in data)
        self.assertTrue('unicore_frontend_ffl_za-access.log' in data)
        self.assertTrue('unicore_frontend_ffl_za-error.log' in data)
        self.assertTrue(
            '/var/praekelt/unicore-cms-ffl/unicorecmsffl/static/' in data)
        self.assertTrue(frontend_socket_path in data)

    @override_settings(DEPLOY_ENVIRONMENT='prod')
    def test_write_frontend_nginx_configs_prod(self):
        nm = self.get_nginx_manager()
        nm.write_frontend_nginx('ffl', 'za', 'some.domain.com')

        frontend_nginx_config_path = os.path.join(
            settings.NGINX_CONFIGS_PATH,
            'frontend_ffl_za.conf')

        with open(frontend_nginx_config_path, "r") as config_file:
            data = config_file.read()
        self.assertTrue(
            'server_name za.ffl.hub.unicore.io some.domain.com' in data)
        self.assertTrue('za.ffl.hub.unicore.io' in data)

        self.addCleanup(lambda: os.remove(frontend_nginx_config_path))

    def test_write_cms_nginx_configs(self):
        nm = self.get_nginx_manager()
        nm.write_cms_nginx('ffl', 'za', 'cms.domain.com')

        cms_nginx_config_path = os.path.join(
            settings.NGINX_CONFIGS_PATH,
            'cms_ffl_za.conf')

        cms_socket_path = os.path.join(
            settings.CMS_SOCKETS_PATH,
            'ffl_za.socket')

        self.assertTrue(os.path.exists(cms_nginx_config_path))

        with open(cms_nginx_config_path, "r") as config_file:
            data = config_file.read()

        self.addCleanup(lambda: os.remove(cms_nginx_config_path))

        self.assertTrue('cms.za.ffl.qa-hub.unicore.io' in data)
        self.assertTrue(
            'server_name cms.za.ffl.qa-hub.unicore.io cms.domain.com' in data)
        self.assertTrue('unicore_cms_django_ffl_za-access.log' in data)
        self.assertTrue('unicore_cms_django_ffl_za-error.log' in data)
        self.assertTrue(cms_socket_path in data)

    @override_settings(DEPLOY_ENVIRONMENT='prod')
    def test_write_cms_nginx_configs_prod(self):
        nm = self.get_nginx_manager()
        nm.write_cms_nginx('ffl', 'za', 'cms.domain.com')

        cms_nginx_config_path = os.path.join(
            settings.NGINX_CONFIGS_PATH,
            'cms_ffl_za.conf')

        cms_socket_path = os.path.join(
            settings.CMS_SOCKETS_PATH,
            'ffl_za.socket')

        self.assertTrue(os.path.exists(cms_nginx_config_path))

        with open(cms_nginx_config_path, "r") as config_file:
            data = config_file.read()

        self.addCleanup(lambda: os.remove(cms_nginx_config_path))

        self.assertTrue('cms.za.ffl.hub.unicore.io' in data)
        self.assertTrue(
            'server_name cms.za.ffl.hub.unicore.io cms.domain.com' in data)
        self.assertTrue('unicore_cms_django_ffl_za-access.log' in data)
        self.assertTrue('unicore_cms_django_ffl_za-error.log' in data)
        self.assertTrue(cms_socket_path in data)

    def test_configs_pushed_to_git(self):
        print 'config ws exists: ', os.path.exists(settings.CONFIGS_REPO_PATH)
        print 'config ws exists: ', os.path.exists(
            '%s_remote' % settings.CONFIGS_REPO_PATH)

        remote_ws = self.mk_workspace(
            working_dir='%s_remote' % settings.CONFIGS_REPO_PATH)
        remote_ws.repo.git.checkout('HEAD', b='temp')

        config_ws = self.mk_workspace(working_dir=settings.CONFIGS_REPO_PATH)
        origin = config_ws.repo.create_remote('origin', remote_ws.repo.git_dir)

        branch = config_ws.repo.active_branch
        origin.fetch()
        remote_master = origin.refs.master
        branch.set_tracking_branch(remote_master)

        with self.settings(CONFIGS_REPO_PATH=config_ws.working_dir):
            nm = self.get_nginx_manager()
            nm.write_cms_nginx('ffl', 'za', 'cms.domain.com')

        cms_nginx_config_path = os.path.join(
            config_ws.working_dir,
            'nginx',
            'cms_ffl_za.conf')
        remote_cms_nginx_config_path = os.path.join(
            remote_ws.working_dir,
            'nginx',
            'cms_ffl_za.conf')

        remote_ws.repo.heads.master.checkout()

        print 'config dir: ', os.listdir(config_ws.working_dir)
        print 'remote dir: ', os.listdir(remote_ws.working_dir)
        git_config = os.path.join(config_ws.working_dir, '.git', 'config')
        with open(git_config, "r") as git_config_file:
            git_config_data = git_config_file.read()
            print git_config_data

        self.assertTrue(os.path.exists(cms_nginx_config_path))
        self.assertTrue(os.path.exists(remote_cms_nginx_config_path))

        with open(cms_nginx_config_path, "r") as config_file:
            nginx_data = config_file.read()
        with open(remote_cms_nginx_config_path, "r") as config_file:
            remote_nginx_data = config_file.read()
        self.assertEquals(nginx_data, remote_nginx_data)

        self.addCleanup(lambda: shutil.rmtree(settings.CONFIGS_REPO_PATH))
        self.addCleanup(
            lambda: shutil.rmtree('%s_remote' % settings.CONFIGS_REPO_PATH))
        self.addCleanup(lambda: os.remove(cms_nginx_config_path))
        self.addCleanup(lambda: os.remove(remote_cms_nginx_config_path))
