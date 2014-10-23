import httpretty
import os
import shutil

from django.test import TestCase
from django.conf import settings

from unicoremc.manager import ConfigManager


@httpretty.activate
class ProjectTestCase(TestCase):

    def tearDown(self):
        if os.path.exists(settings.SUPERVISOR_CONFIGS_PATH):
            shutil.rmtree(settings.SUPERVISOR_CONFIGS_PATH)

        if os.path.exists(settings.NGINX_CONFIGS_PATH):
            shutil.rmtree(settings.NGINX_CONFIGS_PATH)

    def test_write_frontend_supervisor_configs(self):
        cm = ConfigManager()
        cm.write_frontend_supervisor('ffl', 'za')

        frontend_supervisor_config_path = os.path.join(
            settings.SUPERVISOR_CONFIGS_PATH,
            'frontend_ffl_za.conf')

        self.assertTrue(os.path.exists(frontend_supervisor_config_path))

        with open(frontend_supervisor_config_path, "r") as config_file:
            data = config_file.read()

        self.assertTrue('program:unicore_frontend_ffl_za' in data)
        self.assertTrue('ffl.production.za.ini' in data)
        self.assertTrue('/var/praekelt/unicore-cms-ffl' in data)

    def test_write_cms_supervisor_configs(self):
        cm = ConfigManager()
        cm.write_cms_supervisor('ffl', 'za')

        cms_supervisor_config_path = os.path.join(
            settings.SUPERVISOR_CONFIGS_PATH,
            'cms_ffl_za.conf')

        self.assertTrue(os.path.exists(cms_supervisor_config_path))

        with open(cms_supervisor_config_path, "r") as config_file:
            data = config_file.read()

        self.assertTrue('program:unicore_cms_ffl_za' in data)
        self.assertTrue('project.ffl_za_settings' in data)
        self.assertTrue('/var/praekelt/unicore-cms-django' in data)

    def test_write_frontend_nginx_configs(self):
        cm = ConfigManager()
        cm.write_frontend_nginx('ffl', 'za')

        frontend_nginx_config_path = os.path.join(
            settings.NGINX_CONFIGS_PATH,
            'frontend_ffl_za.conf')

        self.assertTrue(os.path.exists(frontend_nginx_config_path))

        with open(frontend_nginx_config_path, "r") as config_file:
            data = config_file.read()

        self.assertTrue('za.qa.ffl.unicore.io' in data)
        self.assertTrue('unicore_frontend_ffl_za-access.log' in data)
        self.assertTrue('unicore_frontend_ffl_za-error.log' in data)
        self.assertTrue(
            '/var/praekelt/unicore-cms-ffl/unicorecmsffl/static/' in data)

    def test_write_cms_nginx_configs(self):
        cm = ConfigManager()
        cm.write_cms_nginx('ffl', 'za')

        cms_nginx_config_path = os.path.join(
            settings.NGINX_CONFIGS_PATH,
            'cms_ffl_za.conf')

        self.assertTrue(os.path.exists(cms_nginx_config_path))

        with open(cms_nginx_config_path, "r") as config_file:
            data = config_file.read()

        self.assertTrue('cms.za.qa.ffl.unicore.io' in data)
        self.assertTrue('unicore_cms_django_ffl_za-access.log' in data)
        self.assertTrue('unicore_cms_django_ffl_za-error.log' in data)
