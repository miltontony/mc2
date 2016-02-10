import responses
import pytest

from django.contrib.auth.models import User

from mc2.controllers.base.tests.base import ControllerBaseTestCase
from mc2.controllers.base import exceptions


@pytest.mark.django_db
class ControllerTestCase(ControllerBaseTestCase):
    fixtures = ['test_users.json', 'test_social_auth.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')

    @responses.activate
    def test_create_controller_state(self):
        self.mock_create_marathon_app()

        p = self.mk_controller()
        pw = p.get_builder().workflow
        pw.take_action('create_marathon_app')

        self.assertEquals(p.state, 'done')
        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_create_marathon_app_bad_response(self):
        self.mock_create_marathon_app(404)

        p = self.mk_controller()
        w = p.get_builder().workflow
        with self.assertRaises(exceptions.MarathonApiException):
            w.take_action('create_marathon_app')
