import pytest

from django.contrib.auth.models import User
from django.db.models.signals import post_save

from controllers.base.tests.base import ControllerBaseTestCase
from controllers.base.models import Controller, publish_to_websocket


@pytest.mark.django_db
class ModelsTestCase(ControllerBaseTestCase):
    fixtures = ['test_users.json', 'test_social_auth.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')
        post_save.disconnect(publish_to_websocket, sender=Controller)
        self.maxDiff = None

    def test_get_marathon_app_data(self):
        p = self.mk_project()

        self.assertEquals(p.get_marathon_app_data(), {
            "id": p.app_id,
            "cmd": "ping",
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "ports": [0],
        })
