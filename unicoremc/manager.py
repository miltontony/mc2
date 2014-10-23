import os
from django.template.loader import render_to_string
from django.conf import settings


class ConfigManager(object):
    def __init__(self):
        self.supervisor_dir = settings.SUPERVISOR_CONFIGS_PATH
        self.nginx_dir = settings.NGINX_CONFIGS_PATH
        self.deploy_environment = settings.DEPLOY_ENVIRONMENT

        if not os.path.exists(self.supervisor_dir):
            os.makedirs(self.supervisor_dir)

        if not os.path.exists(self.nginx_dir):
            os.makedirs(self.nginx_dir)

    def write_frontend_supervisor(self, app_type, country):
        frontend_supervisor_content = render_to_string(
            'configs/frontend.supervisor.conf', {
                'app_type': app_type,
                'country': country.lower(),
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

    def write_cms_supervisor(self, app_type, country):
        cms_supervisor_content = render_to_string(
            'configs/cms.supervisor.conf', {
                'app_type': app_type,
                'country': country.lower(),
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
        self.settings_dir = settings.SETTINGS_OUTPUT_PATH
        self.deploy_environment = settings.DEPLOY_ENVIRONMENT

        if not os.path.exists(settings.SETTINGS_OUTPUT_PATH):
            os.makedirs(self.settings_dir)

    def write_frontend_settings(
            self, app_type, country, clone_url, available_languages):
        if self.deploy_environment == 'qa':
            raven_dsn = (
                'http://3403146e923c400e9dbdc25f0ca2bf89:'
                '4a9a59b5a75142028f81381e97fb173e@'
                'prd-sentry.za.prk-host.net/70')
        else:
            raven_dsn = (
                'http://ae24b1ca62c14e3187409be94bde6828:'
                'abf0b78210874deba6e58ccac08188b0@'
                'prd-sentry.za.prk-host.net/71')

        languages = []
        for lang in available_languages:
            languages.append("('%s', '%s')" % (lang.get_code(), str(lang)))

        frontend_settings_content = render_to_string(
            'configs/pyramid.ini', {
                'app_type': app_type,
                'country': country.lower(),
                'available_languages': '[%s]' % ', '.join(languages),
                'git_repo_uri': clone_url,
                'raven_dsn_uri': raven_dsn
            }
        )

        filepath = os.path.join(
            self.settings_dir,
            '%(app_type)s.production.%(country)s.ini' % {
                'app_type': app_type,
                'country': country.lower(),
            }
        )

        with open(filepath, 'w') as config_file:
            config_file.write(frontend_settings_content)

    def write_cms_settings(self, app_type, country, clone_url):
        if self.deploy_environment == 'qa':
            raven_dsn = (
                'http://3403146e923c400e9dbdc25f0ca2bf89:'
                '4a9a59b5a75142028f81381e97fb173e@'
                'prd-sentry.za.prk-host.net/70')
        else:
            raven_dsn = (
                'http://ae24b1ca62c14e3187409be94bde6828:'
                'abf0b78210874deba6e58ccac08188b0@'
                'prd-sentry.za.prk-host.net/71')

        cms_settings_content = render_to_string(
            'configs/cms.settings.py', {
                'app_type': app_type,
                'country': country.lower(),
                'git_repo_uri': clone_url,
                'raven_dsn_uri': raven_dsn
            }
        )

        filepath = os.path.join(
            self.settings_dir,
            '%(app_type)s_%(country)s_settings.py' % {
                'app_type': app_type,
                'country': country.lower(),
            }
        )

        with open(filepath, 'w') as config_file:
            config_file.write(cms_settings_content)
