from ostinato.statemachine import State, StateMachine


class Initial(State):
    verbose_name = 'Initial'
    transitions = {'create_repo': 'repo_created'}

    def create_repo(self, **kwargs):
        access_token = kwargs.get('access_token')
        if self.instance:
            self.instance.create_repo(access_token)


class RepoCreated(State):
    verbose_name = 'Public'
    transitions = {'clone_repo': 'repo_cloned'}

    def clone_repo(self, **kwargs):
        if self.instance:
            self.instance.clone_repo()


class RepoCloned(State):
    verbose_name = 'Repo Cloned'
    transitions = {'create_remote': 'remote_created'}

    def create_remote(self, **kwargs):
        if self.instance:
            self.instance.create_remote()


class RemoteCreated(State):
    verbose_name = 'Remote Created'
    transitions = {'merge_remote': 'remote_merged'}

    def merge_remote(self, **kwargs):
        if self.instance:
            self.instance.merge_remote()


class RemoteMerged(State):
    verbose_name = 'Remote Merged'
    transitions = {'create_supervisor': 'supervisor_created'}

    def create_supervisor(self, **kwargs):
        if self.instance:
            self.instance.create_supervisor()


class SupervisorCreated(State):
    verbose_name = 'Supervisor Created'
    transitions = {'create_nginx': 'nginx_created'}

    def create_nginx(self, **kwargs):
        if self.instance:
            self.instance.create_nginx()


class NginxCreated(State):
    verbose_name = 'Nginx Created'
    transitions = {'create_pyramid_settings': 'pyramid_settings_created'}

    def create_pyramid_settings(self, **kwargs):
        if self.instance:
            self.instance.create_pyramid_settings()


class PyramidSettingsCreated(State):
    verbose_name = 'Pyarmid Settings Created'
    transitions = {'create_cms_settings': 'cms_settings_created'}

    def create_cms_settings(self, **kwargs):
        if self.instance:
            self.instance.create_cms_settings()


class CmsSettingsCreated(State):
    verbose_name = 'Cms Settings Created'
    transitions = {'create_db': 'db_created'}

    """
    The aim of this step is to ensure the database is created.
    The Database is only needed by the Django CMS app
    """


class DbCreated(State):
    verbose_name = 'Database Created'
    transitions = {'init_db': 'db_initialized'}

    """
    The aim of this step is to ensure the database is initialized (syncdb)
    This can be facilitated by Sideloader (Hook url)
    The Database is only needed by the Django CMS app
    """


class DbInitialized(State):
    verbose_name = 'Database Initialized'
    transitions = {'init_cms': 'cms_initialized'}

    """
    The aim of this step is to ensure the CMS is initialized by content from
    the Git Repo.
    The Database is only needed by the Django CMS app
    """


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
                    self.instance.save()

    def has_next(self):
        return self.instance and 'done' not in self.instance.state and \
            'destroyed' not in self.instance.state

    def run_all(self, **kwargs):
        while self.has_next():
            self.next(**kwargs)
