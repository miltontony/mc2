from unicoremc.websites.workflows import (
    UnicoreCmsWorkflow, SpringboardWorkflow, IogtWorkflow)


class WebsiteManager(object):

    def __init__(self, project):
        self.project = project

    def build(self, **kwargs):
        raise Exception('not implemented')


class UnicoreCmsWebsiteManager(WebsiteManager):

    def __init__(self, project):
        super(UnicoreCmsWebsiteManager, self).__init__(project)
        self.workflow = UnicoreCmsWorkflow(instance=project)

    def build(self, **kwargs):
        self.workflow.run_all(**kwargs)


class SpringboardWebsiteManager(WebsiteManager):

    def __init__(self, project):
        super(SpringboardWebsiteManager, self).__init__(project)
        self.workflow = SpringboardWorkflow(instance=project)

    def build(self, **kwargs):
        self.workflow.run_all(**kwargs)


class IogtWebsiteManager(WebsiteManager):

    def __init__(self, project):
        super(IogtWebsiteManager, self).__init__(project)
        self.workflow = IogtWorkflow(instance=project)

    def build(self, **kwargs):
        self.workflow.run_all()
