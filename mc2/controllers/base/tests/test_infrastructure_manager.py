import responses

from django.test import TestCase
from django.contrib.auth import get_user_model

from mc2.controllers.base.managers.infrastructure import (
    GeneralInfrastructureManager, InfrastructureError)
from mc2.controllers.base.models import Controller

from mc2.controllers.base.tests.utils import setup_responses_for_logdriver


class GeneralInfrastructureManagerTest(TestCase):

    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user(
            'tester', 'test@example.org', 'tester')
        self.controller = Controller(
            name='Test App', marathon_cmd='ping', owner=user)
        self.controller.save()
        setup_responses_for_logdriver(self.controller)
        self.general_im = GeneralInfrastructureManager()
        self.controller_im = self.controller.infra_manager

    @responses.activate
    def test_get_marathon_app(self):
        app = self.general_im.get_marathon_app(self.controller.app_id)
        self.assertEqual(app['id'], '/%s' % (self.controller.app_id,))

    @responses.activate
    def test_get_marathon_app_tasks(self):
        [task] = self.general_im.get_marathon_app_tasks(self.controller.app_id)
        self.assertEqual(task['appId'], '/%s' % (self.controller.app_id,))
        self.assertEqual(
            task['id'], '%s.the-task-id' % (self.controller.app_id,))
        self.assertEqual(task['ports'], [8898])
        self.assertEqual(task['host'], 'worker-machine-1')

    @responses.activate
    def test_get_marathon_info(self):
        info = self.general_im.get_marathon_info()
        self.assertEqual(info['name'], 'marathon')
        self.assertEqual(info['frameworkId'], 'the-framework-id')

    @responses.activate
    def test_get_worker_info(self):
        worker = self.general_im.get_worker_info('worker-machine-1')
        self.assertEqual(worker['id'], 'worker-machine-id')

    @responses.activate
    def test_get_app_log_info(self):
        [info] = self.general_im.get_app_log_info(self.controller.app_id)
        self.assertEqual(
            info,
            {
                'task_host': 'worker-machine-1',
                'task_id': '%s.the-task-id' % (self.controller.app_id,),
                'task_dir': (
                    'worker-machine-id/frameworks/the-framework-id'
                    '/executors/%s.the-task-id/runs/latest') % (
                        self.controller.app_id,),
            }
        )

    @responses.activate
    def test_get_task_log_info(self):
        info = self.general_im.get_task_log_info(
            self.controller.app_id,
            '%s.the-task-id' % (self.controller.app_id,),
            'worker-machine-1')
        self.assertEqual(
            info,
            {
                'task_host': 'worker-machine-1',
                'task_id': '%s.the-task-id' % (self.controller.app_id,),
                'task_dir': (
                    'worker-machine-id/frameworks/the-framework-id'
                    '/executors/%s.the-task-id/runs/latest') % (
                        self.controller.app_id,),
            }
        )

    @responses.activate
    def test_controller_infra_manager_get_marathon_app(self):
        app = self.controller_im.get_controller_marathon_app()
        self.assertEqual(app['id'], '/%s' % (self.controller.app_id,))

    @responses.activate
    def test_controller_infra_manager_get_controller_log_info(self):
        [info] = self.controller_im.get_controller_log_info()
        self.assertEqual(
            info,
            {
                'task_host': 'worker-machine-1',
                'task_id': '%s.the-task-id' % (self.controller.app_id,),
                'task_dir': (
                    'worker-machine-id/frameworks/the-framework-id'
                    '/executors/%s.the-task-id/runs/latest') % (
                        self.controller.app_id,),
            }
        )

    @responses.activate
    def test_controller_infra_manager_get_controller_task_log_info(self):
        info = self.controller_im.get_controller_task_log_info(
            '%s.the-task-id' % (self.controller.app_id,))
        self.assertEqual(
            info,
            {
                'task_host': 'worker-machine-1',
                'task_id': '%s.the-task-id' % (self.controller.app_id,),
                'task_dir': (
                    'worker-machine-id/frameworks/the-framework-id'
                    '/executors/%s.the-task-id/runs/latest') % (
                        self.controller.app_id,),
            }
        )

    @responses.activate
    def test_controller_infra_manager_get_controller_non_existent(self):
        self.assertRaises(
            InfrastructureError,
            self.controller_im.get_controller_task_log_info,
            'non-existing-task-id')
