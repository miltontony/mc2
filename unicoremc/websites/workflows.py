from ostinato.statemachine import StateMachine
from unicoremc.websites.states.base import Done, Destroyed
from unicoremc.websites.states import unicorecms_states, iogt_states


class BaseWorkflow(StateMachine):
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


class UnicoreCmsWorkflow(BaseWorkflow):
    state_map = {
        'initial': unicorecms_states.Initial,
        'repo_created': unicorecms_states.RepoCreated,
        'repo_cloned': unicorecms_states.RepoCloned,
        'remote_created': unicorecms_states.RemoteCreated,
        'remote_merged': unicorecms_states.RemoteMerged,
        'repo_pushed': unicorecms_states.RepoPushed,
        'webhook_created': unicorecms_states.WebhookCreated,
        'workspace_initialized': unicorecms_states.WorkspaceInitialized,
        'nginx_created': unicorecms_states.NginxCreated,
        'hub_app_created': unicorecms_states.HubAppCreated,
        'pyramid_settings_created': unicorecms_states.PyramidSettingsCreated,
        'cms_settings_created': unicorecms_states.CmsSettingsCreated,
        'db_created': unicorecms_states.DbCreated,
        'db_initialized': unicorecms_states.DbInitialized,
        'marathon_app_created': unicorecms_states.MarathonAppCreated,
        'done': Done,
        'destroyed': Destroyed,
    }


class SpringboardWorkflow(UnicoreCmsWorkflow):
    pass


class IogtWorkflow(BaseWorkflow):
    state_map = {
        'initial': iogt_states.Initial,
        'hub_app_created': iogt_states.HubAppCreated,
        'pyramid_settings_created': iogt_states.PyramidSettingsCreated,
        'marathon_app_created': iogt_states.MarathonAppCreated,
        'done': Done,
        'destroyed': Destroyed,
    }
