import os

from subprocess import call

from django.template.loader import render_to_string
from django.conf import settings


class ConfigManager(object):
    def __init__(self):
        self.supervisor_dir = settings.SUPERVISOR_CONFIGS_PATH
        self.nginx_dir = settings.NGINX_CONFIGS_PATH
        self.deploy_environment = settings.DEPLOY_ENVIRONMENT
        self.frontend_settings_dir = settings.FRONTEND_SETTINGS_OUTPUT_PATH
        self.sockets_dir = settings.SOCKETS_PATH

        if not os.path.exists(self.sockets_dir):
            os.makedirs(self.sockets_dir)
        if not os.path.exists(self.frontend_settings_dir):
            os.makedirs(self.frontend_settings_dir)

        if not os.path.exists(self.supervisor_dir):
            os.makedirs(self.supervisor_dir)

        if not os.path.exists(self.nginx_dir):
            os.makedirs(self.nginx_dir)

    def write_frontend_supervisor(self, app_type, country, version):
        frontend_supervisor_content = render_to_string(
            'configs/frontend.supervisor.conf', {
                'app_type': app_type,
                'country': country.lower(),
                'version': version,
                'settings_path': os.path.join(
                    self.frontend_settings_dir,
                    '%s.production.%s.ini' % (app_type, country.lower())),
                'socket_path': os.path.join(
                    self.sockets_dir,
                    '%s.%s.socket' % (app_type, country.lower()))
            }
        )

        filepath = os.path.join(
            self.supervisor_dir,
            'frontend_%(app_type)s_%(country)s.conf' % {
                'app_type': app_type,
                'country': country.lower(),
            }
        )

        with open(filepath, 'w') as config_file:
            config_file.write(frontend_supervisor_content)

    def write_cms_supervisor(self, app_type, country, version):
        cms_supervisor_content = render_to_string(
            'configs/cms.supervisor.conf', {
                'app_type': app_type,
                'country': country.lower(),
                'version': version,
                'socket_path': os.path.join(
                    self.sockets_dir,
                    'cms.%s.%s.socket' % (app_type, country.lower()))
            }
        )

        filepath = os.path.join(
            self.supervisor_dir,
            'cms_%(app_type)s_%(country)s.conf' % {
                'app_type': app_type,
                'country': country.lower(),
            }
        )

        with open(filepath, 'w') as config_file:
            config_file.write(cms_supervisor_content)

    def write_frontend_nginx(self, app_type, country):
        frontend_nginx_content = render_to_string(
            'configs/frontend.nginx.conf', {
                'deploy_environment': settings.DEPLOY_ENVIRONMENT,
                'app_type': app_type,
                'country': country.lower(),
                'socket_path': os.path.join(
                    self.sockets_dir,
                    '%s.%s.socket' % (app_type, country.lower()))
            }
        )

        filepath = os.path.join(
            self.nginx_dir,
            'frontend_%(app_type)s_%(country)s.conf' % {
                'app_type': app_type,
                'country': country.lower(),
            }
        )

        with open(filepath, 'w') as config_file:
            config_file.write(frontend_nginx_content)

    def write_cms_nginx(self, app_type, country):
        cms_nginx_content = render_to_string(
            'configs/cms.nginx.conf', {
                'deploy_environment': self.deploy_environment,
                'app_type': app_type,
                'country': country.lower(),
                'socket_path': os.path.join(
                    self.sockets_dir,
                    'cms.%s.%s.socket' % (app_type, country.lower()))
            }
        )

        filepath = os.path.join(
            self.nginx_dir,
            'cms_%(app_type)s_%(country)s.conf' % {
                'app_type': app_type,
                'country': country.lower(),
            }
        )

        with open(filepath, 'w') as config_file:
            config_file.write(cms_nginx_content)


class SettingsManager(object):
    def __init__(self):
        self.frontend_settings_dir = settings.FRONTEND_SETTINGS_OUTPUT_PATH
        self.cms_settings_dir = settings.CMS_SETTINGS_OUTPUT_PATH
        self.deploy_environment = settings.DEPLOY_ENVIRONMENT
        self.sockets_dir = settings.SOCKETS_PATH

        if not os.path.exists(self.sockets_dir):
            os.makedirs(self.sockets_dir)

        if not os.path.exists(self.frontend_settings_dir):
            os.makedirs(self.frontend_settings_dir)

        if not os.path.exists(self.cms_settings_dir):
            os.makedirs(self.cms_settings_dir)

    def write_frontend_settings(
            self, app_type, country, clone_url, available_languages,
            repo_path):
        if self.deploy_environment == 'qa':
            raven_dsn = settings.RAVEN_DSN_FRONTEND_QA
        else:
            raven_dsn = settings.RAVEN_DSN_FRONTEND_PROD

        languages = []
        for lang in available_languages:
            languages.append("('%s', '%s')" % (lang.get_code(), str(lang)))

        frontend_settings_content = render_to_string(
            'configs/pyramid.ini', {
                'app_type': app_type,
                'country': country.lower(),
                'available_languages': '[%s]' % ', '.join(languages),
                'git_repo_uri': clone_url,
                'raven_dsn_uri': raven_dsn,
                'socket_path': os.path.join(
                    self.sockets_dir,
                    '%s.%s.socket' % (app_type, country.lower())),
                'repo_path': repo_path
            }
        )

        filepath = os.path.join(
            self.frontend_settings_dir,
            '%(app_type)s.production.%(country)s.ini' % {
                'app_type': app_type,
                'country': country.lower(),
            }
        )

        with open(filepath, 'w') as config_file:
            config_file.write(frontend_settings_content)

    def write_cms_settings(self, app_type, country, clone_url, repo_path):
        if self.deploy_environment == 'qa':
            raven_dsn = settings.RAVEN_DSN_CMS_QA
        else:
            raven_dsn = settings.RAVEN_DSN_CMS_PROD

        cms_settings_content = render_to_string(
            'configs/cms.settings.py', {
                'app_type': app_type,
                'country': country.lower(),
                'git_repo_uri': clone_url,
                'raven_dsn_uri': raven_dsn,
                'repo_path': repo_path
            }
        )

        filepath = os.path.join(
            self.cms_settings_dir,
            '%(app_type)s_%(country)s_settings.py' % {
                'app_type': app_type,
                'country': country.lower(),
            }
        )

        with open(filepath, 'w') as config_file:
            config_file.write(cms_settings_content)


class DbManager(object):
    call_subprocess = lambda self, *args, **kwargs: call(*args, **kwargs)

    def __init__(self):
        self.unicore_cms_install_dir = settings.UNICORE_CMS_INSTALL_DIR
        self.unicore_cms_python_venv = settings.UNICORE_CMS_PYTHON_VENV

    def create_db(self, app_type, country):
        env = {
            'DJANGO_SETTINGS_MODULE': 'project.%s_%s_settings' % (
                app_type, country.lower()
            )
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
            'DJANGO_SETTINGS_MODULE': 'project.%s_%s_settings' % (
                app_type, country.lower()
            )
        }

        args = [
            self.unicore_cms_python_venv,
            '%s/manage.py' % self.unicore_cms_install_dir,
            'import_from_git',
            '--quiet',
        ]
        self.call_subprocess(args, env=env, cwd=self.unicore_cms_install_dir)
