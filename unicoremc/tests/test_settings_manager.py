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
        afrikaans = Localisation._for('swa_TZ')

        with self.settings(CONFIGS_REPO_PATH=config_ws.working_dir):
            sm = self.get_settings_manager()
            sm.write_frontend_settings(
                'ffl', 'za', 'git://some.repo.com/.git', [english, afrikaans],
                '/path/to/repo/ffl_za/', english, 'UA-some-profile-id')
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
