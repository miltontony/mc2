import pytest
from mc2.controllers.base.tests.base import ControllerBaseTestCase
from mc2.controllers.freebasics.forms import FreeBasicsControllerForm
from mc2.controllers.freebasics.models import FreeBasicsController
from django.contrib.auth.models import User
from django.http import QueryDict


@pytest.mark.django_db
class FreeBasicsControllerFormTestCase(ControllerBaseTestCase):
    fixtures = ['test_users.json', 'test_social_auth.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')
        self.maxDiff = None

    def test__process_data_empty(self):
        form = FreeBasicsControllerForm()
        self.assertIsNone(form._process_data(None))

    def test__process_data(self):
        data = QueryDict(mutable=True)
        data.appendlist('name', 'Test App')
        data.appendlist('selected_template', 'option1')
        form = FreeBasicsControllerForm()
        self.assertIsNotNone(form._process_data(data))

    def test__process_data_error(self):
        data = QueryDict(mutable=True)
        data.appendlist('name', 'Test App')
        data.appendlist('selected_template', 'optio')
        form = FreeBasicsControllerForm()
        self.assertRaises(KeyError, form._process_data, data)

    def test__get_docker_image_name(self):
        for t in FreeBasicsController.TEMPLATE_CHOICES:
            controller = FreeBasicsController.objects.create(
                name='Test App',
                owner=self.user,
                selected_template=t[0],
            )
            controller.save()
            form = FreeBasicsControllerForm(instance=controller)
            self.assertEqual(form._get_docker_image_name(t[0]),
                             "universalcore/" +
                             dict(FreeBasicsController.TEMPLATE_CHOICES)[t[0]])

    def test__get_marathon_cmd(self):
        for t in FreeBasicsController.TEMPLATE_CHOICES:
            controller = FreeBasicsController.objects.create(
                name='Test App',
                owner=self.user,
                selected_template=t[0],
            )
            controller.save()
            form = FreeBasicsControllerForm(instance=controller)
            self.assertRegexpMatches(
                form._get_marathon_cmd(t[0]),
                "./deploy/docker-entrypoint.sh [A-Za-z]+ [A-Za-z]+\.wsgi 8000")
