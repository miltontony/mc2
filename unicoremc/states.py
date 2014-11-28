from ostinato.statemachine import State, StateMachine


class Initial(State):
    verbose_name = 'Initial'
    transitions = {'create_repo': 'repo_created'}

    def create_repo(self, **kwargs):
        access_token = kwargs.get('access_token')
        if self.instance:
            self.instance.create_repo(access_token)


class RepoCreated(State):
    verbose_name = 'Repo created'
    transitions = {'clone_repo': 'repo_cloned'}

    def clone_repo(self, **kwargs):
        if self.instance:
            self.instance.clone_repo()


class RepoCloned(State):
    verbose_name = 'Repo cloned'
    transitions = {'create_remote': 'remote_created'}

    def create_remote(self, **kwargs):
        if self.instance:
            self.instance.create_remote()


class RemoteCreated(State):
    verbose_name = 'Remote created'
    transitions = {'merge_remote': 'remote_merged'}

    def merge_remote(self, **kwargs):
        if self.instance:
            self.instance.merge_remote()


class RemoteMerged(State):
    verbose_name = 'Remote merged'
    transitions = {'push_repo': 'repo_pushed'}

    def push_repo(self, **kwargs):
        if self.instance:
            self.instance.push_repo()


class RepoPushed(State):
    verbose_name = 'Repo pushed to github'
    transitions = {'create_webhook': 'webhook_created'}

    def create_webhook(self, **kwargs):
        access_token = kwargs.get('access_token')
        if self.instance:
            self.instance.create_webhook(access_token)


class WebhookCreated(State):
    verbose_name = 'Webhook created'
    transitions = {'init_workspace': 'workspace_initialized'}

    def init_workspace(self, **kwargs):
        if self.instance:
            self.instance.init_workspace()


class WorkspaceInitialized(State):
    verbose_name = 'Workspace initialized'
    transitions = {'create_vassal': 'vassal_created'}

    def create_vassal(self, **kwargs):
        if self.instance:
            self.instance.create_vassal()


class VassalCreated(State):
    verbose_name = 'Vassal created'
    transitions = {'create_nginx': 'nginx_created'}

    def create_nginx(self, **kwargs):
        if self.instance:
            self.instance.create_nginx()


class NginxCreated(State):
    verbose_name = 'Nginx created'
    transitions = {'create_pyramid_settings': 'pyramid_settings_created'}

    def create_pyramid_settings(self, **kwargs):
        if self.instance:
            self.instance.create_pyramid_settings()


class PyramidSettingsCreated(State):
    verbose_name = 'Pyarmid settings created'
    transitions = {'create_cms_settings': 'cms_settings_created'}

    def create_cms_settings(self, **kwargs):
        if self.instance:
            self.instance.create_cms_settings()


class CmsSettingsCreated(State):
    verbose_name = 'CMS settings created'
    transitions = {'create_db': 'db_created'}

    def create_db(self, **kwargs):
        if self.instance:
            self.instance.create_db()


class DbCreated(State):
    verbose_name = 'Database created'
    transitions = {'init_db': 'db_initialized'}

    def init_db(self, **kwargs):
        if self.instance:
            self.instance.init_db()


class DbInitialized(State):
    verbose_name = 'Database initialized'
    transitions = {'finish': 'done'}


class Done(State):
    verbose_name = 'Ready for use'
    transitions = {'destroy': 'destroyed'}

    def destroy(self, **kwargs):
        if self.instance:
            self.instance.destroy()


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
        'repo_pushed': RepoPushed,
        'webhook_created': WebhookCreated,
        'workspace_initialized': WorkspaceInitialized,
        'vassal_created': VassalCreated,
        'nginx_created': NginxCreated,
        'pyramid_settings_created': PyramidSettingsCreated,
        'cms_settings_created': CmsSettingsCreated,
        'db_created': DbCreated,
        'db_initialized': DbInitialized,
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
