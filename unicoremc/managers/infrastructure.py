from django.conf import settings
from django.http import Http404

import requests


class InfrastructureError(Exception):
    pass


class GeneralInfrastructureManager(object):

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    def get_marathon_app(self, app_id):
        return requests.get('%s/v2/apps/%s' % (
            settings.MESOS_MARATHON_HOST,
            app_id,
        ), headers=self.headers).json()['app']

    def get_marathon_app_tasks(self, app_id):
        return requests.get('%s/v2/apps/%s/tasks' % (
            settings.MESOS_MARATHON_HOST,
            app_id,
        ), headers=self.headers).json()['tasks']

    def get_marathon_info(self):
        return requests.get(
            '%s/v2/info' % (settings.MESOS_MARATHON_HOST,),
            headers=self.headers).json()

    def get_worker_info(self, hostname):
        return requests.get(
            'http://%s:%s/state.json' % (hostname, settings.MESOS_HTTP_PORT),
            headers=self.headers
        ).json()

    def get_app_log_urls(self, app_id):
        marathon_info = self.get_marathon_info()
        urls = []
        for task in self.get_marathon_app_tasks(app_id):
            task_id = task['id']
            task_host = task['host']
            urls.extend(self.get_task_log_urls(
                app_id, task_id, task_host, marathon_info=marathon_info
            ))
        return urls

    def get_task_log_urls(self, app_id, task_id, task_host,
                          marathon_info=None):
        marathon_info = marathon_info or self.get_marathon_info()
        framework_id = marathon_info['frameworkId']
        follower_id = self.get_worker_info(task_host)['id']
        for path in ["stdout", "stderr"]:
            yield (
                "http://%(task_host)s:%(logdriver_port)s/tail"
                "/%(follower_id)s/frameworks/%(framework_id)s/executors"
                "/%(task_id)s/runs/latest/%(path)s" % {
                    'task_host': task_host,
                    'logdriver_port': settings.LOGDRIVER_PORT,
                    'follower_id': follower_id,
                    'framework_id': framework_id,
                    'task_id': task_id,
                    'path': path,
                })


class ProjectInfrastructureManager(GeneralInfrastructureManager):

    def __init__(self, project):
        self.project = project

    def get_project_marathon_app(self):
        return super(ProjectInfrastructureManager, self).get_marathon_app(
            self.project.app_id)

    def get_project_log_urls(self):
        return super(ProjectInfrastructureManager, self).get_app_log_urls(
            self.project.app_id)

    def get_project_task_log_urls(self, task_id):
        tasks = self.get_marathon_app_tasks(self.project.app_id)
        try:
            [task] = filter(lambda t: t['id'] == task_id, tasks)
            return super(ProjectInfrastructureManager, self).get_task_log_urls(
                self.project.app_id, task['id'], task['host'])
        except ValueError:
            raise InfrastructureError('Task not found.')
