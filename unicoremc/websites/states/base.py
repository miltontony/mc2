from ostinato.statemachine import State


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
