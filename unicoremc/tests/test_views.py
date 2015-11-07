import pytest
import responses

from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from controllers.base.models import Controller, publish_to_websocket
from controllers.base.tests.base import ControllerBaseTestCase

from controllers.docker.models import DockerController


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

        post_save.disconnect(publish_to_websocket, sender=Controller)

    @responses.activate
    def test_homepage(self):
        controller = self.mk_controller()

        self.client.login(username='testuser2', password='test')
        resp = self.client.get(reverse('home'))

        self.assertContains(resp, 'Test App')
        self.assertContains(resp, 'Memory Share: 128.0')
        self.assertContains(resp, 'CPU Share: 0.1')
        self.assertContains(resp, 'Num Instances: 1')
        self.assertContains(
            resp,
            '<a href="/base/%s/" class="btn btn-small btn-primary">edit</a>' %
            controller.id)

    @responses.activate
    def test_homepage_with_docker_controller(self):
        self.mk_controller()
        controller = DockerController.objects.create(
            name='Test Docker App',
            owner=self.user,
            marathon_cmd='ping pong',
            docker_image='docker/image',
            port=1234,
            marathon_health_check_path='/health/path/'
        )

        self.client.login(username='testuser2', password='test')
        resp = self.client.get(reverse('home'))

        self.assertContains(resp, 'Test App')
        self.assertContains(resp, 'Memory Share: 128.0')
        self.assertContains(resp, 'CPU Share: 0.1')
        self.assertContains(resp, 'Num Instances: 1')
        self.assertContains(resp, 'Port: 1234')
        self.assertContains(resp, 'Health Path: /health/path/')
        self.assertContains(resp, 'Docker Image: docker/image')
        self.assertContains(
            resp,
            '<a href="/docker/%s/" class="btn btn-small btn-primary">edit</a>'
            % controller.id)

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
        self.assertContains(resp, 'Memory Share: 128.0')
        self.assertContains(resp, 'CPU Share: 0.1')
        self.assertContains(resp, 'Num Instances: 1')
        self.assertContains(
            resp,
            '<a href="/base/%s/" class="btn btn-small btn-primary">edit</a>' %
            controller.id)
