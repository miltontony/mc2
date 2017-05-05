import pytest
import responses
from django.test.client import Client
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from mc2.controllers.base.models import Controller
from mc2.controllers.base.tests.base import ControllerBaseTestCase
from mc2.controllers.docker.models import DockerController
from mc2.organizations.models import Organization
from mc2 import forms


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
    def test_dashboard(self):
        org = Organization.objects.get(slug='foo-org')
        self.mk_controller(controller={
            'marathon_mem': 256.0,
            'marathon_instances': 2,
            'organization': org})
        self.mk_controller(controller={
            'marathon_mem': 512.0,
            'organization': org})
        self.mk_controller(controller={
            'marathon_mem': 1024.0,
            'organization': org})
        self.mk_controller(controller={
            'marathon_mem': 384.0,
            'organization': org})

        self.client.login(username='testuser2', password='test')
        resp = self.client.get(reverse('dashboard'))

        self.assertContains(resp, '>2.38 GB</span>')
        self.assertContains(resp, '<td>4</td>')
        self.assertContains(resp, '<td>2.38 GB</td>')
        self.assertContains(resp, '<td>0.5</td>')

        self.client.get(
            reverse('organizations:select-active', args=('foo-org',)))

        resp = self.client.get(reverse('dashboard'))

        self.assertContains(resp, '>2.38 GB</span>')
        self.assertContains(resp, '<td>512 MB</td>')
        self.assertContains(resp, '<td>1024 MB</td>')
        self.assertContains(resp, '<td>384 MB</td>')
        self.assertNotContains(resp, '<td>256 MB</td>')

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


class CreateAccountViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'testuser', 'test@email.com', '1234')
        self.client = Client()

    def test_login(self):
        response = self.client.get(reverse('login'))
        self.assertContains(response, 'Forgotten your password')
        self.assertContains(response, 'Create account')

    def test_create_account_view(self):
        response = self.client.post(
            reverse('create_account'),
            data={'username': 'tester', 'password1': 'foo',
                  'password2': 'foo', 'first_name': 'foo',
                  'last_name': 'foo', 'email': 'foo@example.com'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'],
                         'http://testserver%s' % reverse('home'))
        self.assertEqual(User.objects.count(), 2)

    def test_create_new_account_form_unique_email(self):
        self.user = User.objects.create_user(
            'foo', 'foo@email.com', '1234')
        form = forms.CreateAccountForm(data={
            'username': 'foo',
            'email': 'foo@email.com',
            'password1': 'foo',
            'password2': 'foo'})
        self.failIf(form.is_valid())
        self.assertEqual(form.errors['email'],
                                    ["This email address is already in use."
                                     " Please supply a different email"
                                     " address."])

    def test_create_account_form_unique_username(self):
        self.user = User.objects.create_user(
            'foo', 'foo@email.com', '1234')
        form = forms.CreateAccountForm(data={
            'username': 'foo',
            'email': 'foo@email.com',
            'password1': 'foo',
            'password2': 'foo'})
        self.failIf(form.is_valid())
        self.assertEqual(form.errors['username'],
                                    ["A user with that username "
                                     "already exists."])

    def test_username_field_is_required(self):
        response = self.client.post(
            reverse('create_account'),
            data={'password1': 'foo',
                  'password2': 'foo',
                  'first_name': 'foo',
                  'last_name': 'foo',
                  'email': 'foo@example.com'})

        self.assertFormError(response, 'form', 'username',
                             ['This field is required.'])

    def test_password_field_is_required(self):
        response = self.client.post(
            reverse('create_account'),
            data={'username': 'foo',
                  'first_name': 'foo',
                  'last_name': 'foo',
                  'email': 'foo@example.com'})

        self.assertFormError(response, 'form', 'password1',
                             ['This field is required.'])

    def test_email_field_is_required(self):
        response = self.client.post(
            reverse('create_account'),
            data={'username': 'tester',
                  'password1': 'foo',
                  'password2': 'foo',
                  'first_name': 'foo',
                  'last_name': 'foo'})

        self.assertFormError(response, 'form', 'email',
                             ['This field is required.'])

    def test_invalid_email(self):
        response = self.client.post(
            reverse('create_account'),
            data={'username': 'tester',
                  'password1': 'foo',
                  'password2': 'foo',
                  'first_name': 'foo',
                  'last_name': 'foo',
                  'email': 'foo@'})

        self.assertFormError(
            response, 'form', 'email', ['Enter a valid email address.'])

    def test_valid_email(self):
        self.client.post(
            reverse('user_settings'),
            data={'username': 'tester',
                  'password1': 'foo',
                  'password2': 'foo',
                  'first_name': 'foo',
                  'last_name': 'foo',
                  'email': 'test@email.com'})

        self.assertEqual(User.objects.get().email,
                         'test@email.com')

    def test_passwords_not_matching(self):
        self.user = User.objects.create_user(
            'foo', 'foo@email.com', '1234')
        form = forms.CreateAccountForm(data={
            'username': 'foo',
            'email': 'foo@email.com',
            'password1': 'foo',
            'password2': '1234'})
        self.failIf(form.is_valid())
        self.assertEqual(form.errors['password2'],
                                    ["The two password fields didn't match."])
