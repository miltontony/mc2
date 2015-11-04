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

    def get_app_log_info(self, app_id):
        """
        Returns a list of task info dicts for logdriver for the given app_id

        :param app_id str: The application id
        :returns: list
        """
        marathon_info = self.get_marathon_info()
        tasks = []
        for task in self.get_marathon_app_tasks(app_id):
            task_id = task['id']
            task_host = task['host']
            tasks.append(self.get_task_log_info(
                app_id, task_id, task_host, marathon_info=marathon_info
            ))
        return tasks

    def get_task_log_info(self, app_id, task_id, task_host,
                          marathon_info=None):
        """
        Returns a dictionary with the task_host and task_dir for logdriver
        logs for the given task_id

        :param app_id str: the application id
        :param task_id str: the task id
        :param task_host str: the host where the task is running
        :param marathon_info dict:
            info dictionary returned from get_marathon_info, optional
        :returns: dict
        """
        marathon_info = marathon_info or self.get_marathon_info()
        framework_id = marathon_info['frameworkId']
        follower_id = self.get_worker_info(task_host)['id']
        return {
            'task_id': task_id,
            'task_host': task_host,
            'task_dir': (
                "%(follower_id)s/frameworks/%(framework_id)s/executors"
                "/%(task_id)s/runs/latest") % {
                    'follower_id': follower_id,
                    'framework_id': framework_id,
                    'task_id': task_id}
        }


class ControllerInfrastructureManager(GeneralInfrastructureManager):

    def __init__(self, controller):
        """
        A helper manager to get to a controller's marathon app entries

        :param controller Controller: A Controller model instance
        """
        self.controller = controller

    def get_controller_marathon_app(self):
        """
        Returns the data dictionary for the current controller's app_id.

        :returns: dict
        """
        return super(ControllerInfrastructureManager, self).get_marathon_app(
            self.controller.app_id)

    def get_controller_marathon_tasks(self):
        """
        Returns the task list for the current controller's app_id

        :returns: list
        """
        return super(
            ControllerInfrastructureManager, self).get_marathon_app_tasks(
                self.controller.app_id)

    def get_controller_log_info(self):
        """
        Returns all the tasks log URLs for the current controller's app_id

        :returns: list
        """
        return super(ControllerInfrastructureManager, self).get_app_log_info(
            self.controller.app_id)

    def get_controller_task_log_info(self, task_id):
        """
        Returns the log URLs for a given task for the current controller's
        app_id.
        Raises an InfrastructureError if task for task_id not found.

        :param task_id str: the task id
        :returns: list
        """
        tasks = self.get_marathon_app_tasks(self.controller.app_id)
        try:
            [task] = filter(lambda t: t['id'] == task_id, tasks)
            return super(ControllerInfrastructureManager, self).\
                get_task_log_info(
                    self.controller.app_id, task['id'], task['host'])
        except ValueError:
            raise InfrastructureError('Task not found.')
