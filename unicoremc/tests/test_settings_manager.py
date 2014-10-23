import httpretty
import os
import shutil

from django.test import TestCase
from django.conf import settings

from unicoremc.manager import SettingsManager
from unicoremc.models import Localisation


@httpretty.activate
class SettingsManagerTestCase(TestCase):

    def tearDown(self):
        if os.path.exists(settings.SETTINGS_OUTPUT_PATH):
            shutil.rmtree(settings.SETTINGS_OUTPUT_PATH)

    def test_write_frontend_settings(self):
        english = Localisation._for('eng_UK')
        afrikaans = Localisation._for('swh_TZ')
        cm = SettingsManager()
        cm.write_frontend_settings(
            'ffl', 'za', 'http://some.repo.com/.git', [english, afrikaans])

        frontend_settings_path = os.path.join(
            settings.SETTINGS_OUTPUT_PATH,
            'ffl.production.za.ini')

        self.assertTrue(os.path.exists(frontend_settings_path))

        with open(frontend_settings_path, "r") as config_file:
            data = config_file.read()

        self.assertTrue('egg:unicore-cms-ffl' in data)
        self.assertTrue(
            "[('eng_UK', 'English (United Kingdom)')"
            ", ('swh_TZ', 'Swahili (Tanzania)')]" in data)
        self.assertTrue('/ffl_za/' in data)
        self.assertTrue('http://some.repo.com/.git' in data)
