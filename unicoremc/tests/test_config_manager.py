import os

from django.test import TestCase
from django.conf import settings

from unicoremc.manager import ConfigManager


class ConfigManagerTestCase(TestCase):

    def test_write_frontend_nginx_configs(self):
        cm = ConfigManager()
        cm.write_frontend_nginx('ffl', 'za')

        frontend_nginx_config_path = os.path.join(
            settings.NGINX_CONFIGS_PATH,
            'frontend_ffl_za.conf')

        socket_path = os.path.join(
            settings.SOCKETS_PATH,
            'ffl.production.za.socket')

        self.assertTrue(os.path.exists(frontend_nginx_config_path))

        with open(frontend_nginx_config_path, "r") as config_file:
            data = config_file.read()

        self.addCleanup(lambda: os.remove(frontend_nginx_config_path))

        self.assertTrue('za.ffl.qa-hub.unicore.io' in data)
        self.assertTrue('unicore_frontend_ffl_za-access.log' in data)
        self.assertTrue('unicore_frontend_ffl_za-error.log' in data)
        self.assertTrue(
            '/var/praekelt/unicore-cms-ffl/unicorecmsffl/static/' in data)
        self.assertTrue(socket_path in data)

    def test_write_cms_nginx_configs(self):
        cm = ConfigManager()
        cm.write_cms_nginx('ffl', 'za')

        cms_nginx_config_path = os.path.join(
            settings.NGINX_CONFIGS_PATH,
            'cms_ffl_za.conf')

        socket_path = os.path.join(
            settings.SOCKETS_PATH,
            'ffl_za_settings.socket')

        self.assertTrue(os.path.exists(cms_nginx_config_path))

        with open(cms_nginx_config_path, "r") as config_file:
            data = config_file.read()

        self.addCleanup(lambda: os.remove(cms_nginx_config_path))

        self.assertTrue('cms.za.ffl.qa-hub.unicore.io' in data)
        self.assertTrue('unicore_cms_django_ffl_za-access.log' in data)
        self.assertTrue('unicore_cms_django_ffl_za-error.log' in data)
        self.assertTrue(socket_path in data)
