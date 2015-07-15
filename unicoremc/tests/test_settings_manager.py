import os
import shutil

from ConfigParser import ConfigParser

from django.test.utils import override_settings
from django.conf import settings

from unicoremc.models import Localisation
from unicoremc.tests.base import UnicoremcTestCase


class SettingsManagerTestCase(UnicoremcTestCase):

    def test_write_frontend_settings(self):
        english = Localisation._for('eng_GB')
        swahili = Localisation._for('swa_TZ')
        hub_app = self.mk_hub_app()
        sm = self.get_settings_manager()
        sm.write_frontend_settings(
            'ffl', 'za', [english, swahili], english, 'UA-some-profile-id',
            hub_app, 'unicore-cms-content-ffl-za')

        frontend_settings_path = os.path.join(
            settings.CONFIGS_REPO_PATH,
            sm.get_frontend_settings_path('ffl', 'za'))

        self.assertTrue(os.path.exists(frontend_settings_path))

        with open(frontend_settings_path, "r") as config_file:
            data = config_file.read()

        self.addCleanup(lambda: os.remove(frontend_settings_path))

        self.assertTrue('egg:unicore-cms-ffl' in data)
        self.assertTrue(
            "[(u'eng_GB', u'English')"
            ", (u'swa_TZ', u'Swahili')]" in data)
        self.assertTrue('pyramid.default_locale_name = eng_GB' in data)
        self.assertTrue('ga.profile_id = UA-some-profile-id' in data)
        self.assertTrue('es.index_prefix = unicore-cms-content-ffl-za' in data)
        self.assertTrue('thumbor.security_key = some-key' in data)
        self.assertTrue('raven-qa' in data)
        self.assertIn('unicorehub.app_id = %s' % hub_app.get('uuid'), data)
        self.assertIn('unicorehub.app_key = %s' % hub_app.get('key'), data)
        self.assertIn(
            'unicorehub.host = %s' % settings.HUBCLIENT_SETTINGS['host'], data)
        self.assertIn('unicorehub.redirect_to_https = \n', data)

        # check that Hub settings aren't present if hub_app is None
        sm.write_frontend_settings(
            'ffl', 'za', [english, swahili], english, 'UA-some-profile-id',
            None, 'unicore-cms-content-ffl-za')
        with open(frontend_settings_path, "r") as config_file:
            data = config_file.read()

        for key in ('host', 'app_id', 'app_key', 'redirect_to_https'):
            self.assertNotIn('unicorehub.%s' % key, data)

    @override_settings(DEPLOY_ENVIRONMENT='prod')
    def test_write_frontend_settings_prod(self):
        english = Localisation._for('eng_GB')
        swahili = Localisation._for('swa_TZ')
        hub_app = self.mk_hub_app()
        sm = self.get_settings_manager()
        sm.write_frontend_settings(
            'ffl', 'za', [english, swahili], english, 'UA-some-profile-id',
            hub_app, 'unicore-cms-content-ffl-za')

        frontend_settings_path = os.path.join(
            settings.CONFIGS_REPO_PATH,
            sm.get_frontend_settings_path('ffl', 'za'))

        with open(frontend_settings_path, "r") as config_file:
            data = config_file.read()

        self.addCleanup(lambda: os.remove(frontend_settings_path))
        self.assertTrue('raven-prod' in data)
        self.assertTrue('thumbor.security_key = some-key' in data)

    def test_write_cms_settings(self):
        sm = self.get_settings_manager()
        sm.write_cms_settings(
            'ffl', 'za', 'http://some.repo.com/.git',
            '/path/to/repo/ffl_za/')

        cms_settings_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.py')

        self.assertTrue(os.path.exists(cms_settings_path))

        cms_settings_output_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.py')

        self.assertTrue(os.path.exists(cms_settings_output_path))

        with open(cms_settings_path, "r") as config_file:
            data = config_file.read()

        with open(cms_settings_output_path, "r") as config_file:
            data2 = config_file.read()

        self.addCleanup(lambda: os.remove(cms_settings_path))

        self.assertTrue('django_cms_ffl_za' in data)
        self.assertTrue(
            "ELASTIC_GIT_INDEX_PREFIX = 'unicore_cms_ffl_za'" in data)
        self.assertTrue("/path/to/repo/ffl_za" in data)
        self.assertTrue('http://some.repo.com/.git' in data)
        self.assertTrue('raven-cms-qa' in data)
        self.assertEqual(data, data2)

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

        cms_settings_output_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.py')

        self.assertTrue(os.path.exists(cms_settings_output_path))

        with open(cms_settings_path, "r") as config_file:
            data = config_file.read()

        with open(cms_settings_output_path, "r") as config_file:
            data2 = config_file.read()

        self.addCleanup(lambda: os.remove(cms_settings_path))

        self.assertTrue('raven-cms-prod' in data)
        self.assertEqual(data, data2)

    def test_write_cms_config(self):
        sm = self.get_settings_manager()
        sm.write_cms_config(
            'ffl', 'za', 'http://some.repo.com/.git',
            '/path/to/repo/ffl_za/')

        cms_config_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')

        self.assertTrue(os.path.exists(cms_config_path))

        cms_config_output_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')

        self.assertTrue(os.path.exists(cms_config_output_path))

        cp = ConfigParser()
        with open(cms_config_path, "r") as fp:
            cp.readfp(fp)

        cp2 = ConfigParser()
        with open(cms_config_output_path, "r") as fp:
            cp2.readfp(fp)

        self.assertEqual(
            cp.get('uwsgi', 'env'),
            'DJANGO_SETTINGS_MODULE=project.ffl_za')
        self.assertEqual(
            cp2.get('uwsgi', 'env'),
            'DJANGO_SETTINGS_MODULE=project.ffl_za')
        self.assertTrue(cp.get('uwsgi', 'idle'))
        self.assertTrue(cp2.get('uwsgi', 'idle'))

    def test_configs_pushed_to_git(self):
        remote_ws = self.mk_workspace(
            working_dir='%s_remote' % settings.CONFIGS_REPO_PATH)
        remote_repo = remote_ws.repo
        remote_repo.git.checkout('HEAD', b='temp')

        config_ws = self.mk_workspace(working_dir=settings.CONFIGS_REPO_PATH)
        origin = config_ws.repo.create_remote('origin', remote_ws.working_dir)

        branch = config_ws.repo.active_branch
        origin.fetch()
        remote_master = origin.refs.master
        branch.set_tracking_branch(remote_master)

        config_ws.fast_forward()

        english = Localisation._for('eng_GB')
        swahili = Localisation._for('swa_TZ')
        hub_app = self.mk_hub_app()

        with self.settings(CONFIGS_REPO_PATH=config_ws.working_dir):
            sm = self.get_settings_manager()
            sm.write_frontend_settings(
                'ffl', 'za', [english, swahili], english,
                'UA-some-profile-id', hub_app,
                'unicore-cms-content-ffl-za')
            sm.write_cms_settings(
                'ffl', 'za', 'http://some.repo.com/.git',
                '/path/to/repo/ffl_za/')
            sm.write_cms_config(
                'ffl', 'za', 'http://some.repo.com/.git',
                '/path/to/repo/ffl_za/')

        remote_repo.heads.master.checkout()

        frontend_settings_config_path = os.path.join(
            config_ws.working_dir, 'frontend_settings', 'ffl_za.ini')
        remote_frontend_settings_config_path = os.path.join(
            remote_ws.working_dir, 'frontend_settings', 'ffl_za.ini')

        cms_settings_config_path = os.path.join(
            config_ws.working_dir, 'cms_settings', 'ffl_za.py')
        remote_cms_settings_config_path = os.path.join(
            remote_ws.working_dir, 'cms_settings', 'ffl_za.py')

        cms_config_path = os.path.join(
            config_ws.working_dir, 'cms_settings', 'ffl_za.ini')
        remote_cms_config_path = os.path.join(
            remote_ws.working_dir, 'cms_settings', 'ffl_za.ini')

        self.assertTrue(os.path.exists(cms_settings_config_path))
        self.assertTrue(os.path.exists(remote_cms_settings_config_path))
        self.assertTrue(os.path.exists(frontend_settings_config_path))
        self.assertTrue(os.path.exists(remote_frontend_settings_config_path))
        self.assertTrue(os.path.exists(cms_config_path))
        self.assertTrue(os.path.exists(remote_cms_config_path))

        with open(frontend_settings_config_path, "r") as config_file:
            config_data = config_file.read()
        with open(remote_frontend_settings_config_path, "r") as config_file:
            remote_config_data = config_file.read()
        self.assertEquals(config_data, remote_config_data)

        with open(cms_settings_config_path, "r") as config_file:
            config_data = config_file.read()
        with open(remote_cms_settings_config_path, "r") as config_file:
            remote_config_data = config_file.read()
        self.assertEquals(config_data, remote_config_data)

        with open(cms_config_path, "r") as config_file:
            config_data = config_file.read()
        with open(remote_cms_config_path, "r") as config_file:
            remote_config_data = config_file.read()
        self.assertEquals(config_data, remote_config_data)

        self.addCleanup(lambda: shutil.rmtree(settings.CONFIGS_REPO_PATH))
        self.addCleanup(
            lambda: shutil.rmtree('%s_remote' % settings.CONFIGS_REPO_PATH))
        self.addCleanup(lambda: os.remove(cms_config_path))
        self.addCleanup(lambda: os.remove(remote_cms_config_path))
        self.addCleanup(lambda: os.remove(cms_settings_config_path))
        self.addCleanup(lambda: os.remove(remote_cms_settings_config_path))
        self.addCleanup(lambda: os.remove(frontend_settings_config_path))
        self.addCleanup(
            lambda: os.remove(remote_frontend_settings_config_path))

    def test_configs_destroyed(self):
        remote_ws = self.mk_workspace(
            working_dir='%s_remote' % settings.CONFIGS_REPO_PATH)
        remote_repo = remote_ws.repo
        remote_repo.git.checkout('HEAD', b='temp')

        config_ws = self.mk_workspace(working_dir=settings.CONFIGS_REPO_PATH)
        origin = config_ws.repo.create_remote('origin', remote_ws.working_dir)

        branch = config_ws.repo.active_branch
        origin.fetch()
        remote_master = origin.refs.master
        branch.set_tracking_branch(remote_master)

        config_ws.fast_forward()

        english = Localisation._for('eng_GB')
        afrikaans = Localisation._for('swa_TZ')
        hub_app = self.mk_hub_app()

        with self.settings(CONFIGS_REPO_PATH=config_ws.working_dir):
            sm = self.get_settings_manager()
            sm.write_frontend_settings(
                'ffl', 'za', [english, afrikaans],
                english, 'UA-some-profile-id', hub_app,
                'unicore-cms-content-ffl-za')
            sm.write_springboard_settings(
                'ffl', 'za', [english, afrikaans], english,
                'UA-some-profile-id', hub_app,
                ['unicore-cms-content-ffl-za'])
            sm.write_cms_settings(
                'ffl', 'za', 'http://some.repo.com/.git',
                '/path/to/repo/ffl_za/')
            sm.write_cms_config(
                'ffl', 'za', 'http://some.repo.com/.git',
                '/path/to/repo/ffl_za/')

        remote_repo.heads.master.checkout()

        frontend_settings_config_path = os.path.join(
            config_ws.working_dir, 'frontend_settings', 'ffl_za.ini')
        remote_frontend_settings_config_path = os.path.join(
            remote_ws.working_dir, 'frontend_settings', 'ffl_za.ini')

        springboard_settings_config_path = os.path.join(
            config_ws.working_dir, 'springboard_settings', 'ffl_za.ini')
        remote_springboard_settings_config_path = os.path.join(
            remote_ws.working_dir, 'springboard_settings', 'ffl_za.ini')

        cms_settings_config_path = os.path.join(
            config_ws.working_dir, 'cms_settings', 'ffl_za.py')
        remote_cms_settings_config_path = os.path.join(
            remote_ws.working_dir, 'cms_settings', 'ffl_za.py')

        cms_config_path = os.path.join(
            config_ws.working_dir, 'cms_settings', 'ffl_za.ini')
        remote_cms_config_path = os.path.join(
            remote_ws.working_dir, 'cms_settings', 'ffl_za.ini')

        cms_settings_output_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.py')
        cms_config_output_path = os.path.join(
            settings.CMS_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')

        self.assertTrue(os.path.exists(cms_settings_config_path))
        self.assertTrue(os.path.exists(remote_cms_settings_config_path))
        self.assertTrue(os.path.exists(frontend_settings_config_path))
        self.assertTrue(os.path.exists(remote_frontend_settings_config_path))
        self.assertTrue(os.path.exists(cms_config_path))
        self.assertTrue(os.path.exists(remote_cms_config_path))
        self.assertTrue(os.path.exists(cms_settings_output_path))
        self.assertTrue(os.path.exists(cms_config_output_path))

        remote_repo.heads.temp.checkout()
        sm.destroy('ffl', 'za')
        sm.destroy_unicore_cms_settings('ffl', 'za')
        sm.destroy_springboard_settings('ffl', 'za')
        remote_repo.heads.master.checkout()
        self.assertFalse(os.path.exists(cms_settings_config_path))
        self.assertFalse(os.path.exists(remote_cms_settings_config_path))
        self.assertFalse(os.path.exists(frontend_settings_config_path))
        self.assertFalse(os.path.exists(remote_frontend_settings_config_path))
        self.assertFalse(os.path.exists(springboard_settings_config_path))
        self.assertFalse(
            os.path.exists(remote_springboard_settings_config_path))
        self.assertFalse(os.path.exists(cms_config_path))
        self.assertFalse(os.path.exists(remote_cms_config_path))
        self.assertFalse(os.path.exists(cms_settings_output_path))
        self.assertFalse(os.path.exists(cms_config_output_path))

        self.addCleanup(lambda: shutil.rmtree(settings.CONFIGS_REPO_PATH))
        self.addCleanup(
            lambda: shutil.rmtree('%s_remote' % settings.CONFIGS_REPO_PATH))

    def test_write_springboard_settings(self):
        english = Localisation._for('eng_GB')
        swahili = Localisation._for('swa_TZ')
        hub_app = self.mk_hub_app()
        sm = self.get_settings_manager()
        sm.write_springboard_settings(
            'ffl', 'za', [english, swahili], english,
            'UA-some-profile-id', hub_app,
            ['unicore-cms-content-ffl-za', 'unicore-cms-content-gem-uk'])

        springboard_settings_path = os.path.join(
            settings.CONFIGS_REPO_PATH,
            sm.get_springboard_settings_path('ffl', 'za'))

        self.assertTrue(os.path.exists(springboard_settings_path))

        with open(springboard_settings_path, "r") as config_file:
            data = config_file.read()

        self.addCleanup(lambda: os.remove(springboard_settings_path))

        self.assertTrue('egg:springboard_ffl' in data)
        self.assertTrue('pyramid.default_locale_name = eng_GB' in data)
        self.assertTrue('swa_TZ' in data)
        self.assertTrue(
            'unicore.content_repo_urls =\n'
            '    http://testserver:6543/repos/unicore-cms-content-ffl-za.json'
            '\n'
            '    http://testserver:6543/repos/unicore-cms-content-gem-uk.json'
            in data)
        self.assertTrue('es.host = http://localhost:9200' in data)
        self.assertTrue('ga.profile_id = UA-some-profile-id' in data)
        self.assertTrue('thumbor.security_key = some-key' in data)
        self.assertTrue('raven-qa' in data)
        self.assertIn('unicorehub.app_id = %s' % hub_app.get('uuid'), data)
        self.assertIn('unicorehub.app_key = %s' % hub_app.get('key'), data)
        self.assertIn(
            'unicorehub.host = %s' % settings.HUBCLIENT_SETTINGS['host'], data)
        self.assertIn('unicorehub.redirect_to_https = \n', data)

        # check that Hub settings aren't present if hub_app is None
        sm.write_springboard_settings(
            'ffl', 'za', [english, swahili], english,
            'UA-some-profile-id', None, ['unicore-cms-content-ffl-za'])
        with open(springboard_settings_path, "r") as config_file:
            data = config_file.read()

        for key in ('host', 'app_id', 'app_key', 'redirect_to_https'):
            self.assertNotIn('unicorehub.%s' % key, data)
