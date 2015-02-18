import os

from django.conf import settings
from django.test.utils import override_settings

from unicoremc.tests.base import UnicoremcTestCase


class ConfigManagerTestCase(UnicoremcTestCase):

    def test_write_frontend_nginx_configs(self):
        cm = self.get_config_manager()

        cm.write_frontend_nginx('ffl', 'za', 'some.domain.com')

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
        cm = self.get_config_manager()
        cm.write_frontend_nginx('ffl', 'za', 'some.domain.com')

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
        cm = self.get_config_manager()
        cm.write_cms_nginx('ffl', 'za', 'cms.domain.com')

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
        cm = self.get_config_manager()
        cm.write_cms_nginx('ffl', 'za', 'cms.domain.com')

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
