import json

import responses

from django.test import TestCase

from unicoremc.managers.infrastructure import GeneralInfrastructureManager


class GeneralInfrastructureManagerTest(TestCase):

    def setUp(self):
        responses.add(
            responses.GET, 'http://testserver:8080/v2/apps/foo',
            status=200, content_type='application/json',
            body=json.dumps({
                "app": {
                    "id": "/foo"
                }
            }))

        responses.add(
            responses.GET, 'http://testserver:8080/v2/apps/foo/tasks',
            status=200, content_type='application/json',
            body=json.dumps({
                "tasks": [{
                    "appId": "/foo",
                    "id": "foo.the-task-id",
                    "host": "worker-machine-1",
                    "ports": [8898],
                    "startedAt": "2015-08-10T16:09:43.561Z",
                    "stagedAt": "2015-08-10T16:09:35.436Z",
                    "version": "2015-07-31T15:41:42.894Z",
                    "healthCheckResults": [],
                }]
            }))

        responses.add(
            responses.GET, 'http://testserver:8080/v2/info',
            status=200, content_type='application/json',
            body=json.dumps({
                "name": "marathon",
                "frameworkId": "the-framework-id",
            }))

        responses.add(
            responses.GET, 'http://worker-machine-1:5555/state.json',
            status=200, content_type='application/json',
            body=json.dumps({
                "id": "worker-machine-id",
            })
        )
        self.im = GeneralInfrastructureManager()

    def tearDown(self):
        pass

    @responses.activate
    def test_get_marathon_app(self):
        app = self.im.get_marathon_app('foo')
        self.assertEqual(app['id'], '/foo')

    @responses.activate
    def test_get_marathon_app_tasks(self):
        [task] = self.im.get_marathon_app_tasks('foo')
        self.assertEqual(task['appId'], '/foo')
        self.assertEqual(
            task['id'], 'foo.the-task-id')
        self.assertEqual(task['ports'], [8898])
        self.assertEqual(task['host'], 'worker-machine-1')

    @responses.activate
    def test_get_marathon_info(self):
        info = self.im.get_marathon_info()
        self.assertEqual(info['name'], 'marathon')
        self.assertEqual(info['frameworkId'], 'the-framework-id')

    @responses.activate
    def test_get_worker_info(self):
        worker = self.im.get_worker_info('worker-machine-1')
        self.assertEqual(worker['id'], 'worker-machine-id')

    @responses.activate
    def test_get_log_urls(self):
        urls = list(self.im.get_log_urls('foo'))
        self.assertEqual(
            urls,
            [('http://worker-machine-1:3333/tail'
              '/worker-machine-id/frameworks/the-framework-id'
              '/executors/foo.the-task-id/runs/latest/stdout'),
             ('http://worker-machine-1:3333/tail'
              '/worker-machine-id/frameworks/the-framework-id'
              '/executors/foo.the-task-id/runs/latest/stderr'),
             ])
