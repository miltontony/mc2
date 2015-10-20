from ostinato.statemachine import State


class Done(State):
    verbose_name = 'Ready for use'
    transitions = {'destroy': 'destroyed', 'suspend': 'suspended'}

    def destroy(self, **kwargs):
        if self.instance:
            self.instance.destroy()


class Suspended(State):
    verbose_name = 'Suspended'
    transitions = {'activate': 'done'}


class Destroyed(State):
    verbose_name = 'Destroyed'
    transitions = {}
