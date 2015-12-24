from mc2.controllers.base.workflows import Workflow


class Builder(object):

    def __init__(self, project):
        self.project = project
        self.workflow = Workflow(instance=project)

    def build(self, **kwargs):
        self.workflow.run_all(**kwargs)
