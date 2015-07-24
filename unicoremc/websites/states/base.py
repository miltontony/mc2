from ostinato.statemachine import State


class Done(State):
    verbose_name = 'Ready for use'
    transitions = {'destroy': 'destroyed'}

    def destroy(self, **kwargs):
        if self.instance:
            self.instance.destroy()


class Destroyed(State):
    verbose_name = 'Destroyed'
    transitions = {}
