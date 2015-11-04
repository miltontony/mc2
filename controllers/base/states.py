from ostinato.statemachine import State


class Initial(State):
    verbose_name = 'Initial'
    transitions = {'create_marathon_app': 'done'}

    def create_marathon_app(self, **kwargs):
        if self.instance:
            self.instance.create_marathon_app()


class Done(State):
    verbose_name = 'Ready for use'
    transitions = {'destroy': 'destroyed', 'missing': 'missing'}

    def destroy(self, **kwargs):
        if self.instance:
            self.instance.destroy()


class Missing(State):
    verbose_name = 'Missing'
    transitions = {'activate': 'done'}


class Destroyed(State):
    verbose_name = 'Destroyed'
    transitions = {}
