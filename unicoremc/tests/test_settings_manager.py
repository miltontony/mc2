import os
from ConfigParser import ConfigParser

from django.test.utils import override_settings
from django.conf import settings

from unicoremc.models import Localisation
from unicoremc.tests.base import UnicoremcTestCase


class SettingsManagerTestCase(UnicoremcTestCase):

    def test_write_frontend_settings(self):
        english = Localisation._for('eng_GB')
        afrikaans = Localisation._for('swa_TZ')
        sm = self.get_settings_manager()
        sm.write_frontend_settings(
            'ffl', 'za', 'git://some.repo.com/.git', [english, afrikaans],
            '/path/to/repo/ffl_za/', english, 'UA-some-profile-id')

        frontend_settings_path = os.path.join(
            settings.FRONTEND_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')

        socket_path = os.path.join(
            settings.FRONTEND_SOCKETS_PATH,
            'ffl_za.socket')

        self.assertTrue(os.path.exists(frontend_settings_path))

        with open(frontend_settings_path, "r") as config_file:
            data = config_file.read()

        self.addCleanup(lambda: os.remove(frontend_settings_path))

        self.assertTrue('egg:unicore-cms-ffl' in data)
        self.assertTrue(
            "[(u'eng_GB', u'English')"
            ", (u'swa_TZ', u'Swahili')]" in data)
        self.assertTrue('/ffl_za/' in data)
        self.assertTrue('es.index_prefix = unicore_frontend_ffl_za' in data)
        self.assertTrue('git://some.repo.com/.git' in data)
        self.assertTrue(socket_path in data)
        self.assertTrue('pyramid.default_locale_name = eng_GB' in data)
        self.assertTrue('ga.profile_id = UA-some-profile-id' in data)
        self.assertTrue('raven-qa' in data)

    @override_settings(DEPLOY_ENVIRONMENT='prod')
    def test_write_frontend_settings_prod(self):
        english = Localisation._for('eng_GB')
        afrikaans = Localisation._for('swa_TZ')
        sm = self.get_settings_manager()
        sm.write_frontend_settings(
            'ffl', 'za', 'git://some.repo.com/.git', [english, afrikaans],
            '/path/to/repo/ffl_za/', english, 'UA-some-profile-id')

        frontend_settings_path = os.path.join(
            settings.FRONTEND_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')

        with open(frontend_settings_path, "r") as config_file:
            data = config_file.read()

        self.addCleanup(lambda: os.remove(frontend_settings_path))
        self.assertTrue('raven-prod' in data)

    def test_write_cms_settings(self):
        sm = self.get_settings_manager()
        sm.write_cms_settings(
            'ffl', 'za', 'http://some.repo.com/.git',
            '/path/to/repo/ffl_za/')

        cms_settings_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.py')

        self.assertTrue(os.path.exists(cms_settings_path))

        with open(cms_settings_path, "r") as config_file:
            data = config_file.read()

        self.addCleanup(lambda: os.remove(cms_settings_path))

        self.assertTrue('django_cms_ffl_za' in data)
        self.assertTrue(
            "ELASTIC_GIT_INDEX_PREFIX = 'unicore_cms_ffl_za'" in data)
        self.assertTrue("/path/to/repo/ffl_za" in data)
        self.assertTrue('http://some.repo.com/.git' in data)
        self.assertTrue('raven-cms-qa' in data)

    @override_settings(DEPLOY_ENVIRONMENT='prod')
    def test_write_cms_settings_prod(self):
        sm = self.get_settings_manager()
        sm.write_cms_settings(
            'ffl', 'za', 'http://some.repo.com/.git',
            '/path/to/repo/ffl_za/')

        cms_settings_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.py')

        self.assertTrue(os.path.exists(cms_settings_path))

        with open(cms_settings_path, "r") as config_file:
            data = config_file.read()

        self.addCleanup(lambda: os.remove(cms_settings_path))

        self.assertTrue('raven-cms-prod' in data)

    def test_write_cms_config(self):
        sm = self.get_settings_manager()
        sm.write_cms_config(
            'ffl', 'za', 'http://some.repo.com/.git',
            '/path/to/repo/ffl_za/')

        cms_config_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')

        self.assertTrue(os.path.exists(cms_config_path))

        cp = ConfigParser()
        with open(cms_config_path, "r") as fp:
            cp.readfp(fp)

        self.assertEqual(
            cp.get('uwsgi', 'env'),
            'DJANGO_SETTINGS_MODULE=project.ffl_za')
        self.assertTrue(cp.get('uwsgi', 'idle'))
