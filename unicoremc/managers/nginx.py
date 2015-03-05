import os

from django.template.loader import render_to_string
from django.conf import settings

from elasticgit import EG

from unicoremc.tasks import push_to_git


class NginxManager(object):
    def __init__(self):
        self.deploy_environment = settings.DEPLOY_ENVIRONMENT
        self.nginx_dir = 'nginx/'
        self.frontend_settings_dir = 'frontend_settings/'
        self.frontend_sockets_dir = 'frontend_sockets/'
        self.cms_sockets_dir = 'cms_sockets/'
        self.workspace = EG.workspace(settings.CONFIGS_REPO_PATH)

        self.dirs = [
            self.frontend_sockets_dir,
            self.cms_sockets_dir,
            self.frontend_settings_dir,
            self.nginx_dir,
        ]
        for dir_ in self.dirs:
            if not os.path.isdir(dir_):
                os.makedirs(dir_)

    def get_deploy_name(self, app_type, country):
        return '%s_%s' % (app_type.lower(), country.lower(),)

    def get_frontend_nginx_path(self, app_type, country):
        return os.path.join(
            self.workspace.working_dir,
            self.nginx_dir,
            'frontend_%s.conf' % (self.get_deploy_name(app_type, country),)
        )

    def get_cms_nginx_path(self, app_type, country):
        return os.path.join(
            self.workspace.working_dir,
            self.nginx_dir,
            'cms_%s.conf' % (self.get_deploy_name(app_type, country),)
        )

    def destroy(self, app_type, country):
        self.workspace.sm.delete_data(
            self.get_frontend_nginx_path(app_type, country),
            'Deleting frontend nginx config for %s_%s' % (app_type, country))
        self.workspace.sm.delete_data(
            self.get_cms_nginx_path(app_type, country),
            'Deleting cms nginx config for %s_%s' % (app_type, country))
        push_to_git.delay(self.workspace.working_dir)

    def write_frontend_nginx(self, app_type, country, frontend_custom_domain):
        frontend_nginx_content = render_to_string(
            'configs/frontend.nginx.conf', {
                'deploy_environment': settings.DEPLOY_ENVIRONMENT,
                'app_type': app_type,
                'country': country.lower(),
                'frontend_custom_domain': frontend_custom_domain,
                'socket_path': os.path.join(
                    self.workspace.working_dir,
                    self.frontend_sockets_dir,
                    '%s.socket' % (self.get_deploy_name(app_type, country),)),
            }
        )

        filepath = self.get_frontend_nginx_path(app_type, country)

        self.workspace.sm.store_data(
            filepath, frontend_nginx_content,
            'Save frontend nginx config for %s_%s' % (app_type, country))
        push_to_git.delay(self.workspace.working_dir)

    def write_cms_nginx(self, app_type, country, cms_custom_domain):
        cms_nginx_content = render_to_string(
            'configs/cms.nginx.conf', {
                'deploy_environment': self.deploy_environment,
                'app_type': app_type,
                'country': country.lower(),
                'cms_custom_domain': cms_custom_domain,
                'socket_path': os.path.join(
                    self.workspace.working_dir,
                    self.cms_sockets_dir,
                    '%s.socket' % (self.get_deploy_name(app_type, country),))
            }
        )

        filepath = self.get_cms_nginx_path(app_type, country)

        self.workspace.sm.store_data(
            filepath, cms_nginx_content,
            'Save cms nginx config for %s_%s' % (app_type, country))
        push_to_git.delay(self.workspace.working_dir)
