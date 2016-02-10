import pytest
import responses

from django.contrib.auth.models import User

from mc2.controllers.base.tests.base import ControllerBaseTestCase


@pytest.mark.django_db
class StatesTestCase(ControllerBaseTestCase):
    fixtures = ['test_users.json', 'test_social_auth.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')

    def test_initial_state(self):
        controller = self.mk_controller()
        self.assertEquals(controller.state, 'initial')

    @responses.activate
    def test_finish_state(self):
        self.mock_create_marathon_app()
        p = self.mk_controller()
        pw = p.get_builder().workflow
        pw.take_action('create_marathon_app')
        self.assertEquals(p.state, 'done')

    @responses.activate
    def test_next(self):
        self.mock_create_marathon_app()
        controller = self.mk_controller()
        self.assertEquals(controller.state, 'initial')

        w = controller.get_builder().workflow
        w.next()
        self.assertEquals(controller.state, 'done')

    @responses.activate
    def test_automation_using_next(self):
        self.mock_create_marathon_app()

        controller = self.mk_controller()

        self.assertEquals(controller.state, 'initial')

        w = controller.get_builder().workflow
        w.run_all()

        self.assertEquals(controller.state, 'done')

    @responses.activate
    def test_missing_state(self):
        self.mock_create_marathon_app()
        controller = self.mk_controller()

        self.assertEquals(controller.state, 'initial')

        w = controller.get_builder().workflow
        w.run_all()

        self.assertEquals(controller.state, 'done')

        # nothing should happen on next
        w.next()
        self.assertEquals(controller.state, 'done')

        w.take_action('missing')
        self.assertEquals(controller.state, 'missing')

        w.take_action('activate')
        self.assertEquals(controller.state, 'done')

        w.take_action('destroy')
        self.assertEquals(controller.state, 'destroyed')
