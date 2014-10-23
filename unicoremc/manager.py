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
