import json
import responses

from django.test import TransactionTestCase
from django.conf import settings


class ControllerBaseTestCase(TransactionTestCase):

    def mock_create_marathon_app(self, status=201):
        responses.add(
            responses.POST, '%s/v2/apps' % settings.MESOS_MARATHON_HOST,
            body=json.dumps({}),
            content_type="application/json",
            status=status)

    def mock_update_marathon_app(self, app_type, country, app_id, status=200):
        responses.add(
            responses.PUT, '%s/v2/apps/%s-%s-%s' % (
                settings.MESOS_MARATHON_HOST, app_type, country, app_id),
            body=json.dumps({}),
            content_type="application/json",
            status=status)

    def mock_restart_marathon_app(self, project, status=200):
        responses.add(
            responses.POST, '%s/v2/apps/%s/restart' % (
                settings.MESOS_MARATHON_HOST, project.app_id),
            body=json.dumps({}),
            content_type="application/json",
            status=status)
