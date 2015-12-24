from ostinato.statemachine import StateMachine
from mc2.controllers.base.states import Initial, Done, Destroyed, Missing


class Workflow(StateMachine):
    initial_state = 'initial'
    state_map = {
        'initial': Initial,
        'done': Done,
        'missing': Missing,
        'destroyed': Destroyed,
    }

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
