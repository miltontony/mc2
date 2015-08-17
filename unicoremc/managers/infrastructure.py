from django.conf import settings

import requests


class InfrastructureError(Exception):
    pass


class GeneralInfrastructureManager(object):

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    def get_marathon_app(self, app_id):
        """
        Returns the data dictionary for the given app_id

        :param app_id str: The application id
        :returns: dict
        """
        return requests.get('%s/v2/apps/%s' % (
            settings.MESOS_MARATHON_HOST,
            app_id,
        ), headers=self.headers).json()['app']

    def get_marathon_app_tasks(self, app_id):
        """
        Returns the list of tasks for the given app_id

        :param app_id str: The application id
        :returns: list
        """
        return requests.get('%s/v2/apps/%s/tasks' % (
            settings.MESOS_MARATHON_HOST,
            app_id,
        ), headers=self.headers).json()['tasks']

    def get_marathon_info(self):
        """
        Returns information on the Marathon host

        :returns: dict
        """
        return requests.get(
            '%s/v2/info' % (settings.MESOS_MARATHON_HOST,),
            headers=self.headers).json()

    def get_worker_info(self, hostname):
        """
        Returns info for the worker at the given hostname.

        :returns: dict
        """
        return requests.get(
            'http://%s:%s/state.json' % (hostname, settings.MESOS_HTTP_PORT),
            headers=self.headers
        ).json()

    def get_app_log_urls(self, app_id):
        """
        Returns a list of log URLs for logdriver for the given app_id

        :param app_id str: The application id
        :returns: list
        """
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
        """
        Returns a list of log URLs for logdriver for the given task_id

        :param app_id str: the application id
        :param task_id str: the task id
        :param task_host str: the host where the task is running
        :param marathon_info dict:
            info dictionary returned from get_marathon_info, optional
        :returns: generator
        """
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
        """
        A helper manager to get to a project's marathon app entries

        :param project Project: A Project model instance
        """
        self.project = project

    def get_project_marathon_app(self):
        """
        Returns the data dictionary for the current project's app_id.

        :returns: dict
        """
        return super(ProjectInfrastructureManager, self).get_marathon_app(
            self.project.app_id)

    def get_project_marathon_tasks(self):
        """
        Returns the task list for the current project's app_id

        :returns: list
        """
        return super(
            ProjectInfrastructureManager, self).get_marathon_app_tasks(
                self.project.app_id)

    def get_project_log_urls(self):
        """
        Returns all the tasks log URLs for the current project's app_id

        :returns: list
        """
        return super(ProjectInfrastructureManager, self).get_app_log_urls(
            self.project.app_id)

    def get_project_task_log_urls(self, task_id):
        """
        Returns the log URLs for a given task for the current project's app_id.
        Raises an InfrastructureError if task for task_id not found.

        :param task_id str: the task id
        :returns: list
        """
        tasks = self.get_marathon_app_tasks(self.project.app_id)
        try:
            [task] = filter(lambda t: t['id'] == task_id, tasks)
            return super(ProjectInfrastructureManager, self).get_task_log_urls(
                self.project.app_id, task['id'], task['host'])
        except ValueError:
            raise InfrastructureError('Task not found.')
