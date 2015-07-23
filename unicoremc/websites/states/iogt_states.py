from ostinato.statemachine import State


class Initial(State):
    verbose_name = 'Initial'
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
    transitions = {'create_marathon_app': 'marathon_app_created'}

    def create_marathon_app(self, **kwargs):
        if self.instance:
            self.instance.create_marathon_app()


class MarathonAppCreated(State):
    verbose_name = 'Marathon app created'
    transitions = {'finish': 'done'}
