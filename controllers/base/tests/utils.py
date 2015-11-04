import json

import responses


def setup_responses_for_logdriver(controller):
    responses.add(
        responses.GET,
        'http://testserver:8080/v2/apps/%s' % (controller.app_id,),
        status=200, content_type='application/json',
        body=json.dumps({
            "app": {
                "id": "/%s" % (controller.app_id,),
            }
        }))

    responses.add(
        responses.GET,
        'http://testserver:8080/v2/apps/%s/tasks' % (controller.app_id,),
        status=200, content_type='application/json',
        body=json.dumps({
            "tasks": [{
                "appId": "/%s" % (controller.app_id,),
                "id": "%s.the-task-id" % (controller.app_id,),
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
