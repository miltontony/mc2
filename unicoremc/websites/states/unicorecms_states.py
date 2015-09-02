from ostinato.statemachine import State


class Initial(State):
    verbose_name = 'Initial'
    transitions = {'create_repo': 'repo_created'}

    def create_repo(self, **kwargs):
        if self.instance:
            self.instance.create_repo()


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
        if self.instance:
            self.instance.create_webhook()
            self.instance.create_webhook(
                self.instance.apollo_frontend_url())


class WebhookCreated(State):
    verbose_name = 'Webhook created'
    transitions = {'init_workspace': 'workspace_initialized'}

    def init_workspace(self, **kwargs):
        if self.instance:
            self.instance.init_workspace()


class WorkspaceInitialized(State):
    verbose_name = 'Workspace initialized'
    transitions = {'create_nginx': 'nginx_created'}

    def create_nginx(self, **kwargs):
        if self.instance:
            self.instance.create_nginx()


class NginxCreated(State):
    verbose_name = 'Nginx created'
    transitions = {'create_hub_app': 'hub_app_created'}

    def create_hub_app(self, **kwargs):
        if self.instance:
            self.instance.create_or_update_hub_app()


class HubAppCreated(State):
    verbose_name = 'Hub app created'
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
    transitions = {'create_marathon_app': 'marathon_app_created'}

    def create_marathon_app(self, **kwargs):
        if self.instance:
            self.instance.create_marathon_app()


class MarathonAppCreated(State):
    verbose_name = 'Marathon app created'
    transitions = {'finish': 'done'}
