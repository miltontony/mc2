from ostinato.statemachine import State, StateMachine


class Initial(State):
    verbose_name = 'Initial'
    transitions = {'destroy': 'destroyed', 'create_repo': 'repo_created'}

    def create_repo(self, **kwargs):
        if self.instance:
            # TODO: call requests and create a repo
            self.instance.repo_url = (
                'http://new-git-repo/user/'
                'unicore-cms-content-%(app_type)s-%(country)s.git' %
            {
                'app_type': self.instance.app_type,
                'country': self.instance.country.lower(),
            })


class RepoCreated(State):
    verbose_name = 'Public'
    transitions = {'destroy': 'destroyed', 'clone_repo': 'repo_cloned'}


class RepoCloned(State):
    verbose_name = 'Repo Cloned'
    transitions = {'destroy': 'destroyed', 'create_remote': 'remote_created'}


class RemoteCreated(State):
    verbose_name = 'Remote Created'
    transitions = {'destroy': 'destroyed', 'merge_remote': 'remote_merged'}


class RemoteMerged(State):
    verbose_name = 'Remote Merged'
    transitions = {
        'destroy': 'destroyed',
        'create_supervisor': 'supervisor_created'}


class SupervisorCreated(State):
    verbose_name = 'Supervisor Created'
    transitions = {'destroy': 'destroyed', 'create_nginx': 'nginx_created'}


class NginxCreated(State):
    verbose_name = 'Nginx Created'
    transitions = {
        'destroy': 'destroyed',
        'create_pyramid_settings': 'pyarmid_settings_created'}


class PyramidSettingsCreated(State):
    verbose_name = 'Pyarmid Settings Created'
    transitions = {
        'destroy': 'destroyed',
        'create_cms_settings': 'cms_settings_created'}


class CmsSettingsCreated(State):
    verbose_name = 'Cms Settings Created'
    transitions = {'destroy': 'destroyed', 'create_db': 'db_created'}


class DbCreated(State):
    verbose_name = 'Database Created'
    transitions = {'destroy': 'destroyed', 'init_db': 'db_initialized'}


class DbInitialized(State):
    verbose_name = 'Database Initialized'
    transitions = {'destroy': 'destroyed', 'init_cms': 'cms_initialized'}


class CmsInitialized(State):
    verbose_name = 'CMS Initialized'
    transitions = {
        'destroy': 'destroyed',
        'reload_supervisor': 'supervisor_reloaded'}


class SupervisorReloaded(State):
    verbose_name = 'Supervisor Reloaded'
    transitions = {'destroy': 'destroyed', 'reload_nginx': 'nginx_reloaded'}


class NginxReloaded(State):
    verbose_name = 'Database Initialized'
    transitions = {'destroy': 'destroyed', 'finish': 'done'}


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
        'pyarmid_settings_created': PyramidSettingsCreated,
        'cms_settings_created': CmsSettingsCreated,
        'db_created': DbCreated,
        'db_initialized': DbInitialized,
        'cms_initialized': CmsInitialized,
        'supervisor_reloaded': SupervisorReloaded,
        'nginx_reloaded': NginxReloaded,
        'done': Done,
    }
    initial_state = 'initial'
