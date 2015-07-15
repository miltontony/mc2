import os

from subprocess import call

from django.conf import settings

from unicoremc.utils import remove_if_exists


class DbManager(object):
    call_subprocess = lambda self, *args, **kwargs: call(*args, **kwargs)

    def __init__(self):
        self.unicore_cms_install_dir = settings.UNICORE_CMS_INSTALL_DIR
        self.unicore_cms_python_venv = settings.UNICORE_CMS_PYTHON_VENV

    def destroy(self, app_type, country):
        remove_if_exists(os.path.join(
            self.unicore_cms_install_dir,
            'django_cms_%s_%s.db' % (app_type, country.lower())
        ))

    def get_deploy_name(self, app_type, country):
        return '%s_%s' % (app_type.lower(), country.lower(),)

    def create_db(self, app_type, country):
        env = {
            'DJANGO_SETTINGS_MODULE': 'project.%s' % self.get_deploy_name(
                app_type, country)
        }

        args = [
            self.unicore_cms_python_venv,
            '%s/manage.py' % self.unicore_cms_install_dir,
            'syncdb',
            '--migrate',
            '--noinput',
        ]
        self.call_subprocess(args, env=env, cwd=self.unicore_cms_install_dir)

    def init_db(self, app_type, country):
        env = {
            'DJANGO_SETTINGS_MODULE': 'project.%s' % self.get_deploy_name(
                app_type, country)
        }

        args = [
            self.unicore_cms_python_venv,
            '%s/manage.py' % self.unicore_cms_install_dir,
            'import_from_git',
            '--quiet',
        ]
        self.call_subprocess(args, env=env, cwd=self.unicore_cms_install_dir)
