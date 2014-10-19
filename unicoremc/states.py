import requests
from ostinato.statemachine import State, StateMachine

from django.conf import settings
from unicoremc import constants


class GithubApiException(Exception):
    pass


class AccessTokenRequiredException(Exception):
    pass


class Initial(State):
    verbose_name = 'Initial'
    transitions = {'create_repo': 'repo_created'}

    def create_repo(self, **kwargs):
        if self.instance:
            new_repo_name = constants.NEW_REPO_NAME_FORMAT % {
                'app_type': self.instance.app_type,
                'country': self.instance.country.lower(),
                'suffix': settings.GITHUB_REPO_NAME_SUFFIX}

            access_token = kwargs.get('access_token')
            post_data = {
                "name": new_repo_name,
                "description": "A Unicore CMS content repo for %s %s" % (
                    self.instance.app_type, self.instance.country),
                "homepage": "https://github.com",
                "private": False,
                "has_issues": True
            }

            if access_token:
                headers = {'Authorization': 'token %s' % access_token}
                resp = requests.post(
                    settings.GITHUB_API + 'repos',
                    json=post_data,
                    headers=headers)

                if resp.status_code != 201:
                    raise GithubApiException(
                        'Create repo failed with response: %s - %s' %
                        (resp.status_code, resp.json().get('message')))

                self.instance.repo_url = resp.json().get('clone_url')
            else:
                raise AccessTokenRequiredException('access_token is required')


class RepoCreated(State):
    verbose_name = 'Public'
    transitions = {'clone_repo': 'repo_cloned'}


class RepoCloned(State):
    verbose_name = 'Repo Cloned'
    transitions = {'create_remote': 'remote_created'}


class RemoteCreated(State):
    verbose_name = 'Remote Created'
    transitions = {'merge_remote': 'remote_merged'}


class RemoteMerged(State):
    verbose_name = 'Remote Merged'
    transitions = {'create_supervisor': 'supervisor_created'}


class SupervisorCreated(State):
    verbose_name = 'Supervisor Created'
    transitions = {'create_nginx': 'nginx_created'}


class NginxCreated(State):
    verbose_name = 'Nginx Created'
    transitions = {'create_pyramid_settings': 'pyramid_settings_created'}


class PyramidSettingsCreated(State):
    verbose_name = 'Pyarmid Settings Created'
    transitions = {'create_cms_settings': 'cms_settings_created'}


class CmsSettingsCreated(State):
    verbose_name = 'Cms Settings Created'
    transitions = {'create_db': 'db_created'}


class DbCreated(State):
    verbose_name = 'Database Created'
    transitions = {'init_db': 'db_initialized'}


class DbInitialized(State):
    verbose_name = 'Database Initialized'
    transitions = {'init_cms': 'cms_initialized'}


class CmsInitialized(State):
    verbose_name = 'CMS Initialized'
    transitions = {'reload_supervisor': 'supervisor_reloaded'}


class SupervisorReloaded(State):
    verbose_name = 'Supervisor Reloaded'
    transitions = {'reload_nginx': 'nginx_reloaded'}


class NginxReloaded(State):
    verbose_name = 'Database Initialized'
    transitions = {'finish': 'done'}


class Done(State):
    verbose_name = 'Done'
    transitions = {'destroy': 'destroyed'}


class Destroyed(State):
    verbose_name = 'Destroyed'
    transitions = {}


class ProjectWorkflow(StateMachine):
    state_map = {
        'initial': Initial,
        'destroyed': Destroyed,
        'repo_created': RepoCreated,
        'repo_cloned': RepoCloned,
        'remote_created': RemoteCreated,
        'remote_merged': RemoteMerged,
        'supervisor_created': SupervisorCreated,
        'nginx_created': NginxCreated,
        'pyramid_settings_created': PyramidSettingsCreated,
        'cms_settings_created': CmsSettingsCreated,
        'db_created': DbCreated,
        'db_initialized': DbInitialized,
        'cms_initialized': CmsInitialized,
        'supervisor_reloaded': SupervisorReloaded,
        'nginx_reloaded': NginxReloaded,
        'done': Done,
    }
    initial_state = 'initial'

    def next(self, **kwargs):
        if self.instance:
            for action in self.actions:
                if self.has_next():
                    self.take_action(action, **kwargs)

    def has_next(self):
        return self.instance and 'done' not in self.instance.state and \
            'destroyed' not in self.instance.state

    def run_all(self, **kwargs):
        while self.has_next():
            self.next(**kwargs)
