import pytest
import responses

from django.contrib.auth.models import User
from django.db.models.signals import post_save

from controllers.base.tests.base import ControllerBaseTestCase
from controllers.base.models import Controller, publish_to_websocket
from controllers.base import exceptions


@pytest.mark.django_db
class ModelsTestCase(ControllerBaseTestCase):
    fixtures = ['test_users.json', 'test_social_auth.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')
        post_save.disconnect(publish_to_websocket, sender=Controller)
        self.maxDiff = None

    def test_get_marathon_app_data(self):
        controller = self.mk_controller()
        self.assertEquals(controller.get_marathon_app_data(), {
            "id": controller.app_id,
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "cmd": "ping",
        })

    @responses.activate
    def test_update_marathon_marathon_exception(self):
        controller = self.mk_controller()
        self.mock_update_marathon_app(controller.app_id, 404)
        with self.assertRaises(exceptions.MarathonApiException):
            controller.update_marathon_app()

    @responses.activate
    def test_restart_marathon_marathon_exception(self):
        controller = self.mk_controller()
        self.mock_restart_marathon_app(controller.app_id, 404)
        with self.assertRaises(exceptions.MarathonApiException):
            controller.marathon_restart_app()

    @responses.activate
    def test_marathon_app_exists(self):
        controller = self.mk_controller()

        self.mock_exists_on_marathon(controller.app_id)
        self.assertTrue(controller.exists_on_marathon())

    @responses.activate
    def test_marathon_app_does_not_exist(self):
        controller = self.mk_controller()

        self.mock_exists_on_marathon(controller.app_id, 404)
        self.assertFalse(controller.exists_on_marathon())
