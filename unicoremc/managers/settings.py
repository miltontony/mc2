import os

from django.template.loader import render_to_string
from django.conf import settings

from unicoremc.tasks import push_to_git


class SettingsManager(object):
    def __init__(self):
        self.frontend_settings_dir = 'frontend_settings/'
        self.cms_settings_dir = 'cms_settings/'
        self.deploy_environment = settings.DEPLOY_ENVIRONMENT
        self.cms_sockets_dir = settings.CMS_SOCKETS_PATH
        self.frontend_sockets_dir = settings.FRONTEND_SOCKETS_PATH

        self.dirs = [
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
        self.workspace.sm.delete_data(
            self.get_frontend_settings_path(app_type, country),
            'Deleted frontend settings config for %s_%s' % (app_type, country))
        self.workspace.sm.delete_data(
            self.get_cms_settings_path(app_type, country),
            'Deleted cms settings config for %s_%s' % (app_type, country))
        self.workspace.sm.delete_data(
            self.get_cms_config_path(app_type, country),
            'Deleted cms config for %s_%s' % (app_type, country))
        push_to_git.delay(self.workspace.working_dir)

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

        self.workspace.sm.store_data(
            filepath, frontend_settings_content,
            'Save frontend settings config for %s_%s' % (app_type, country))
        push_to_git.delay(self.workspace.working_dir)

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

        self.workspace.sm.store_data(
            filepath, cms_settings_content,
            'Save frontend settings config for %s_%s' % (app_type, country))
        push_to_git.delay(self.workspace.working_dir)

    def write_cms_config(self, app_type, country, clone_url, repo_path):
        cms_config_content = render_to_string(
            'configs/cms.config.ini', {
                'cms_settings_dir': self.cms_settings_dir,
                'settings_module': self.get_deploy_name(
                    app_type, country)
            })

        filepath = self.get_cms_config_path(app_type, country)

        self.workspace.sm.store_data(
            filepath, cms_config_content,
            'Save frontend settings config for %s_%s' % (app_type, country))
        push_to_git.delay(self.workspace.working_dir)
