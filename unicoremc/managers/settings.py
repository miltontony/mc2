import os

from django.template.loader import render_to_string
from django.conf import settings

from elasticgit import EG

from unicoremc.tasks import push_to_git
from unicoremc.utils import remove_if_exists, git_remove_if_exists
from unicoremc import constants


class SettingsManager(object):
    def __init__(self):
        self.frontend_settings_dir = 'frontend_settings/'
        self.cms_settings_dir = 'cms_settings/'
        self.springboard_settings_dir = 'springboard_settings/'
        self.cms_settings_output_dir = settings.CMS_SETTINGS_OUTPUT_PATH

        self.deploy_environment = settings.DEPLOY_ENVIRONMENT
        self.cms_sockets_dir = settings.CMS_SOCKETS_PATH
        self.frontend_sockets_dir = settings.FRONTEND_SOCKETS_PATH
        self.workspace = EG.workspace(settings.CONFIGS_REPO_PATH)

        self.dirs = [
            self.cms_sockets_dir,
            self.frontend_sockets_dir,
            self.cms_settings_output_dir,
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

    def get_springboard_settings_path(self, app_type, country):
        return os.path.join(
            self.springboard_settings_dir,
            '%s.ini' % (self.get_deploy_name(app_type, country),)
        )

    def get_cms_settings_path(self, app_type, country):
        return os.path.join(
            self.cms_settings_dir,
            '%s.py' % (self.get_deploy_name(app_type, country),)
        )

    def get_cms_settings_output_path(self, app_type, country):
        return os.path.join(
            self.cms_settings_output_dir,
            '%s.py' % (self.get_deploy_name(app_type, country),)
        )

    def get_cms_config_path(self, app_type, country):
        # NOTE: this needs to match the socket name
        return os.path.join(
            self.cms_settings_dir,
            '%s.ini' % (self.get_deploy_name(app_type, country),)
        )

    def get_cms_config_output_path(self, app_type, country):
        # NOTE: this needs to match the socket name
        return os.path.join(
            self.cms_settings_output_dir,
            '%s.ini' % (self.get_deploy_name(app_type, country),)
        )

    def destroy(self, app_type, country):
        remove_if_exists(self.get_cms_settings_output_path(app_type, country))
        remove_if_exists(self.get_cms_config_output_path(app_type, country))

        git_remove_if_exists(
            self.workspace,
            self.get_cms_settings_path(app_type, country),
            ('Deleted cms settings config for %s_%s'
                % (app_type, country)).encode('utf-8'))
        git_remove_if_exists(
            self.workspace,
            self.get_cms_config_path(app_type, country),
            ('Deleted cms config for %s_%s'
                % (app_type, country)).encode('utf-8'))
        push_to_git.delay(self.workspace.working_dir)

    def destroy_unicore_cms_settings(self, app_type, country):
        self.workspace.sm.delete_data(
            self.get_frontend_settings_path(app_type, country),
            ('Deleted frontend settings config for %s_%s' %
                (app_type, country)).encode('utf-8'))
        push_to_git.delay(self.workspace.working_dir)

    def destroy_springboard_settings(self, app_type, country):
        self.workspace.sm.delete_data(
            self.get_springboard_settings_path(app_type, country),
            ('Deleted springboard settings for %s_%s' % (app_type, country))
            .encode('utf-8'))
        push_to_git.delay(self.workspace.working_dir)

    def write_frontend_settings(
            self, app_type, country, available_languages,
            default_language, ga_profile_id, hub_app):
        if self.deploy_environment == 'qa':
            raven_dsn = settings.RAVEN_DSN_FRONTEND_QA
        else:
            raven_dsn = settings.RAVEN_DSN_FRONTEND_PROD

        repo_name = constants.NEW_REPO_NAME_FORMAT % {
            'app_type': app_type,
            'country': country.lower(),
            'suffix': settings.GITHUB_REPO_NAME_SUFFIX}

        languages = []
        for lang in available_languages:
            languages.append(repr((lang.get_code(), lang.get_display_name())))

        hub_app_id = hub_app.get('uuid') if hub_app else None
        hub_app_key = hub_app.get('key') if hub_app else None

        frontend_settings_content = render_to_string(
            'configs/pyramid.ini', {
                'app_type': app_type,
                'country': country.lower(),
                'available_languages': '[%s]' % ', '.join(languages),
                'default_language': default_language.get_code(),
                'raven_dsn_uri': raven_dsn,
                'ga_profile_id': ga_profile_id,
                'es_host': settings.ELASTICSEARCH_HOST,
                'ucd_host': settings.UNICORE_DISTRIBUTE_HOST,
                'repo_name': repo_name,
                'hub_app_id': hub_app_id,
                'hub_app_key': hub_app_key,
                'hub_settings': settings.HUBCLIENT_SETTINGS
            }
        )

        filepath = self.get_frontend_settings_path(app_type, country)

        self.workspace.sm.store_data(
            filepath, frontend_settings_content,
            'Save frontend settings config for %s_%s'.encode('utf-8') %
            (app_type, country))
        push_to_git.delay(self.workspace.working_dir)

    def write_springboard_settings(
            self, app_type, country, available_languages,
            default_language, ga_profile_id, hub_app):
        if self.deploy_environment == 'qa':
            raven_dsn = settings.RAVEN_DSN_FRONTEND_QA
        else:
            raven_dsn = settings.RAVEN_DSN_FRONTEND_PROD

        repo_name = constants.NEW_REPO_NAME_FORMAT % {
            'app_type': app_type,
            'country': country.lower(),
            'suffix': settings.GITHUB_REPO_NAME_SUFFIX}

        languages = [lang.get_code() for lang in available_languages]

        hub_app_id = hub_app.get('uuid') if hub_app else None
        hub_app_key = hub_app.get('key') if hub_app else None

        content = render_to_string(
            'configs/springboard.ini', {
                'app_type': app_type,
                'country': country.lower(),
                'available_languages': languages,
                'default_language': default_language.get_code(),
                'raven_dsn_uri': raven_dsn,
                'ga_profile_id': ga_profile_id,
                'thumbor_security_key': settings.THUMBOR_SECURITY_KEY,
                'hub_app_id': hub_app_id,
                'hub_app_key': hub_app_key,
                'hub_settings': settings.HUBCLIENT_SETTINGS,
                'es_host': settings.ELASTICSEARCH_HOST,
                'ucd_host': settings.UNICORE_DISTRIBUTE_HOST,
                'repo_name': repo_name,
            }
        )

        filepath = self.get_springboard_settings_path(app_type, country)

        self.workspace.sm.store_data(
            filepath, content,
            ('Save springboard settings config for %s_%s' %
                (app_type, country)).encode('utf-8'))
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

        # Write settings file to git repo
        filepath = self.get_cms_settings_path(app_type, country)
        self.workspace.sm.store_data(
            filepath, cms_settings_content,
            ('Save cms settings config for %s_%s' % (app_type, country))
            .encode('utf-8'))
        push_to_git.delay(self.workspace.working_dir)

        # Write settings file to django config folder
        filepath = self.get_cms_settings_output_path(app_type, country)
        with open(filepath, 'w') as config_file:
            config_file.write(cms_settings_content)

    def write_cms_config(self, app_type, country, clone_url, repo_path):
        cms_config_content = render_to_string(
            'configs/cms.config.ini', {
                'cms_settings_dir': self.cms_settings_dir,
                'settings_module': self.get_deploy_name(
                    app_type, country)
            })

        # Write settings file to git repo
        filepath = self.get_cms_config_path(app_type, country)
        self.workspace.sm.store_data(
            filepath, cms_config_content,
            ('Save cms config for %s_%s' % (app_type, country))
            .encode('utf-8'))
        push_to_git.delay(self.workspace.working_dir)

        # Write settings file to django config folder
        filepath = self.get_cms_config_output_path(app_type, country)
        with open(filepath, 'w') as config_file:
            config_file.write(cms_config_content)
