import pytest
import responses
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from mc2.controllers.base.models import Controller
from mc2.controllers.base.tests.base import ControllerBaseTestCase
from mc2.controllers.docker.models import DockerController


# Unknowm controller for testing the template tag default
class UnknownController(Controller):
    pass


@pytest.mark.django_db
class ViewsTestCase(ControllerBaseTestCase):
    fixtures = [
        'test_users.json', 'test_social_auth.json', 'test_organizations.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='testuser', password='test')
        self.user = User.objects.get(username='testuser')

    @responses.activate
    def test_homepage(self):
        controller = self.mk_controller()

        self.client.login(username='testuser2', password='test')
        resp = self.client.get(reverse('home'))

        self.assertContains(resp, 'Test App')
        self.assertContains(resp, 'Status')
        self.assertContains(resp, 'Edit')
        self.assertContains(resp, 'Delete')
        self.assertContains(
            resp,
            '<a href="/base/%s/">' %
            controller.id)
        controller.delete()

    @responses.activate
    def test_homepage_with_docker_controller(self):
        DockerController.objects.create(
            name='Test Docker App',
            owner=self.user,
            marathon_cmd='ping pong',
            docker_image='docker/image',
            port=1234,
            marathon_health_check_path='/health/path/'
        )

        self.client.login(username='testuser2', password='test')
        resp = self.client.get(reverse('home'))

        self.assertContains(resp, 'Test Docker App')
        self.assertContains(resp, 'Status')
        self.assertContains(resp, 'View')
        self.assertContains(resp, 'Edit')
        self.assertContains(resp, 'Delete')

    @responses.activate
    def test_template_tag_fallback(self):
        controller = UnknownController.objects.create(
            owner=self.user,
            name='Test App',
            marathon_cmd='ping'
        )

        self.client.login(username='testuser2', password='test')
        resp = self.client.get(reverse('home'))

        self.assertContains(resp, 'Test App')

        self.assertContains(
            resp, '<a href="/base/%s/">' % controller.id)

        self.assertContains(
            resp,
            '<a class="text-red" href="/base/delete/%s/">' % controller.id)
