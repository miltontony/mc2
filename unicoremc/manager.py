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
        self.frontend_sockets_dir = settings.FRONTEND_SOCKETS_PATH
        self.cms_sockets_dir = settings.CMS_SOCKETS_PATH

        self.dirs = [
            self.frontend_sockets_dir,
            self.cms_sockets_dir,
            self.frontend_settings_dir,
            self.supervisor_dir,
            self.nginx_dir,
        ]
        for dir_ in self.dirs:
            if not os.path.isdir(dir_):
                os.makedirs(dir_)

    def get_deploy_name(self, app_type, country):
        return '%s_%s' % (app_type.lower(), country.lower(),)

    def get_frontend_nginx_path(self, app_type, country):
        return os.path.join(
            self.nginx_dir,
            'frontend_%s.conf' % (self.get_deploy_name(app_type, country),)
        )

    def get_cms_nginx_path(self, app_type, country):
        return os.path.join(
            self.nginx_dir,
            'cms_%s.conf' % (self.get_deploy_name(app_type, country),)
        )

    def destroy(self, app_type, country):
        os.remove(self.get_frontend_nginx_path(app_type, country))
        os.remove(self.get_cms_nginx_path(app_type, country))

    def write_frontend_nginx(self, app_type, country):
        frontend_nginx_content = render_to_string(
            'configs/frontend.nginx.conf', {
                'deploy_environment': settings.DEPLOY_ENVIRONMENT,
                'app_type': app_type,
                'country': country.lower(),
                'socket_path': os.path.join(
                    self.frontend_sockets_dir,
                    '%s.socket' % (self.get_deploy_name(app_type, country),))
            }
        )

        filepath = self.get_frontend_nginx_path(app_type, country)

        with open(filepath, 'w') as config_file:
            config_file.write(frontend_nginx_content)

    def write_cms_nginx(self, app_type, country):
        cms_nginx_content = render_to_string(
            'configs/cms.nginx.conf', {
                'deploy_environment': self.deploy_environment,
                'app_type': app_type,
                'country': country.lower(),
                'socket_path': os.path.join(
                    self.cms_sockets_dir,
                    '%s.socket' % (self.get_deploy_name(app_type, country),))
            }
        )

        filepath = self.get_cms_nginx_path(app_type, country)

        with open(filepath, 'w') as config_file:
            config_file.write(cms_nginx_content)


class SettingsManager(object):
    def __init__(self):
        self.frontend_settings_dir = settings.FRONTEND_SETTINGS_OUTPUT_PATH
        self.cms_settings_dir = settings.CMS_SETTINGS_OUTPUT_PATH
        self.deploy_environment = settings.DEPLOY_ENVIRONMENT
        self.cms_sockets_dir = settings.CMS_SOCKETS_PATH
        self.frontend_sockets_dir = settings.FRONTEND_SOCKETS_PATH

        self.dirs = [
            self.frontend_settings_dir,
            self.cms_settings_dir,
            self.cms_sockets_dir,
            self.frontend_sockets_dir,
        ]

        for dir_ in self.dirs:
            if not os.path.isdir(dir_):
                os.makedirs(dir_)

    def get_deploy_name(self, app_type, country):
        return '%s_%s' % (app_type.lower(), country.lower(),)

    def get_frontend_settings_path(self, app_type, country):
        return os.path.join(
            self.frontend_settings_dir,
            '%s.ini' % (self.get_deploy_name(app_type, country),)
        )

    def get_cms_settings_path(self, app_type, country):
        return os.path.join(
            self.cms_settings_dir,
            '%s.py' % (self.get_deploy_name(app_type, country),)
        )

    def get_cms_config_path(self, app_type, country):
        # NOTE: this needs to match the socket name
        return os.path.join(
            self.cms_settings_dir,
            '%s.ini' % (self.get_deploy_name(app_type, country),)
        )

    def destroy(self, app_type, country):
        os.remove(self.get_frontend_settings_path(app_type, country))
        os.remove(self.get_cms_settings_path(app_type, country))
        os.remove(self.get_cms_config_path(app_type, country))

    def write_frontend_settings(
            self, app_type, country, clone_url, available_languages,
            repo_path, default_language, ga_profile_id):
        if self.deploy_environment == 'qa':
            raven_dsn = settings.RAVEN_DSN_FRONTEND_QA
        else:
            raven_dsn = settings.RAVEN_DSN_FRONTEND_PROD

        languages = []
        for lang in available_languages:
            languages.append(repr((lang.get_code(), lang.get_display_name())))

        frontend_settings_content = render_to_string(
            'configs/pyramid.ini', {
                'app_type': app_type,
                'country': country.lower(),
                'available_languages': '[%s]' % ', '.join(languages),
                'default_language': default_language.get_code(),
                'git_repo_uri': clone_url,
                'raven_dsn_uri': raven_dsn,
                'socket_path': os.path.join(
                    self.frontend_sockets_dir,
                    '%s.socket' % (self.get_deploy_name(
                        app_type, country.lower()),)),
                'repo_path': repo_path,
                'ga_profile_id': ga_profile_id
            }
        )

        filepath = self.get_frontend_settings_path(app_type, country)
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

        filepath = self.get_cms_settings_path(app_type, country)

        with open(filepath, 'w') as config_file:
            config_file.write(cms_settings_content)

    def write_cms_config(self, app_type, country, clone_url, repo_path):
        cms_config_content = render_to_string(
            'configs/cms.config.ini', {
                'cms_settings_dir': self.cms_settings_dir,
                'settings_module': self.get_deploy_name(
                    app_type, country)
            })

        filepath = self.get_cms_config_path(app_type, country)
        with open(filepath, 'w') as config_file:
            config_file.write(cms_config_content)


class DbManager(object):
    call_subprocess = lambda self, *args, **kwargs: call(*args, **kwargs)

    def __init__(self):
        self.unicore_cms_install_dir = settings.UNICORE_CMS_INSTALL_DIR
        self.unicore_cms_python_venv = settings.UNICORE_CMS_PYTHON_VENV

    def destroy(self, app_type, country):
        os.remove(os.path.join(
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
