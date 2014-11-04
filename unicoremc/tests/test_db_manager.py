from django.test import TestCase

from unicoremc.manager import DbManager


class DbManagerTestCase(TestCase):

    def test_create_db(self):
        def call_mock(*call_args, **call_kwargs):
            cwd = call_kwargs.get('cwd')
            env = call_kwargs.get('env')
            [args] = call_args
            self.assertEqual(cwd, '/path/to/unicore-cms-django')
            self.assertEqual(
                env, {'DJANGO_SETTINGS_MODULE': 'project.ffl_za_settings'})
            self.assertTrue('/path/to/bin/python' in args)
            self.assertTrue(
                '/path/to/unicore-cms-django/manage.py' in args)
            self.assertTrue('syncdb' in args)
            self.assertTrue('--migrate' in args)
            self.assertTrue('--noinput' in args)

        cm = DbManager()

        cm.call_subprocess = call_mock
        cm.create_db('ffl', 'ZA')

    def test_init_db(self):
        def call_mock(*call_args, **call_kwargs):
            cwd = call_kwargs.get('cwd')
            env = call_kwargs.get('env')
            [args] = call_args
            self.assertEqual(cwd, '/path/to/unicore-cms-django')
            self.assertEqual(
                env, {'DJANGO_SETTINGS_MODULE': 'project.ffl_za_settings'})
            self.assertTrue('/path/to/bin/python' in args)
            self.assertTrue(
                '/path/to/unicore-cms-django/manage.py' in args)
            self.assertTrue('import_from_git' in args)
            self.assertTrue('--quiet' in args)

        cm = DbManager()

        cm.call_subprocess = call_mock
        cm.init_db('ffl', 'ZA')
