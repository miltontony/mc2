from django.test import TestCase

from unicoremc.manager import DbManager


class DbManagerTestCase(TestCase):

    def test_create_db(self):
        def call_mock(*call_args, **call_kwargs):
            cwd = call_kwargs.get('cwd')
            [args] = call_args
            self.assertEqual(cwd, '/var/praekelt/unicore-cms-django')
            self.assertTrue(
                "DJANGO_SETTINGS_MODULE='project.ffl_za_settings'" in args)
            self.assertTrue('/var/praekelt/python/bin/python' in args)
            self.assertTrue(
                '/var/praekelt/unicore-cms-django/manage.py' in args)
            self.assertTrue('syncdb' in args)
            self.assertTrue('--migrate' in args)
            self.assertTrue('--noinput' in args)

        cm = DbManager()

        cm.call_subprocess = call_mock
        cm.create_db('ffl', 'ZA')

    def test_init_db(self):
        def call_mock(*call_args, **call_kwargs):
            cwd = call_kwargs.get('cwd')
            [args] = call_args
            self.assertEqual(cwd, '/var/praekelt/unicore-cms-django')
            self.assertTrue(
                "DJANGO_SETTINGS_MODULE='project.ffl_za_settings'" in args)
            self.assertTrue('/var/praekelt/python/bin/python' in args)
            self.assertTrue(
                '/var/praekelt/unicore-cms-django/manage.py' in args)
            self.assertTrue('import_from_git' in args)
            self.assertTrue('--quiet' in args)

        cm = DbManager()

        cm.call_subprocess = call_mock
        cm.init_db('ffl', 'ZA')
