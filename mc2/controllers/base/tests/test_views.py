import os
import pytest
import responses
from django.conf import settings
from django.test import RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from mc2.controllers.base.models import Controller
from mc2.controllers.base.tests.base import ControllerBaseTestCase
from mc2.controllers.base.tests.utils import setup_responses_for_logdriver
from mc2.controllers.base.views import AppEventSourceView
from mc2.organizations.models import Organization, OrganizationUserRelation


@pytest.mark.django_db
class ViewsTestCase(ControllerBaseTestCase):
    fixtures = [
        'test_users.json', 'test_social_auth.json', 'test_organizations.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='testuser', password='test')
        self.user = User.objects.get(username='testuser')

    @responses.activate
    def test_create_new_controller(self):
        existing_controller = self.mk_controller()

        self.client.login(username='testuser2', password='test')
        self.client.get(
            reverse('organizations:select-active', args=('foo-org',)))

        self.mock_create_marathon_app()

        data = {
            'name': 'Another test app',
            'marathon_cmd': 'ping2',
            'env-TOTAL_FORMS': 0,
            'env-INITIAL_FORMS': 0,
            'env-MIN_NUM_FORMS': 0,
            'env-MAX_NUM_FORMS': 100,
            'label-TOTAL_FORMS': 0,
            'label-INITIAL_FORMS': 0,
            'label-MIN_NUM_FORMS': 0,
            'label-MAX_NUM_FORMS': 100,
        }

        response = self.client.post(reverse('base:add'), data)

        self.assertEqual(response.status_code, 302)

        controller = Controller.objects.exclude(
            pk=existing_controller.pk).get()
        self.assertEqual(controller.state, 'done')

        self.assertEqual(controller.name, 'Another test app')
        self.assertEqual(controller.marathon_cmd, 'ping2')
        self.assertEqual(controller.organization.slug, 'foo-org')
        self.assertTrue(controller.slug)

    @responses.activate
    def test_create_new_controller_with_label(self):
        existing_controller = self.mk_controller()

        self.client.login(username='testuser2', password='test')
        self.client.get(
            reverse('organizations:select-active', args=('foo-org',)))

        self.mock_create_marathon_app()

        data = {
            'name': 'Another test app',
            'marathon_cmd': 'ping2',
            'env-TOTAL_FORMS': 0,
            'env-INITIAL_FORMS': 0,
            'env-MIN_NUM_FORMS': 0,
            'env-MAX_NUM_FORMS': 100,
            'label-0-name': 'A_TEST_KEY',
            'label-0-value': 'the value',
            'label-TOTAL_FORMS': 1,
            'label-INITIAL_FORMS': 0,
            'label-MIN_NUM_FORMS': 0,
            'label-MAX_NUM_FORMS': 100,
        }

        response = self.client.post(reverse('base:add'), data)

        self.assertEqual(response.status_code, 302)

        controller = Controller.objects.exclude(
            pk=existing_controller.pk).get()
        self.assertEqual(controller.state, 'done')

        self.assertEqual(controller.name, 'Another test app')
        self.assertEqual(controller.marathon_cmd, 'ping2')
        self.assertEqual(controller.organization.slug, 'foo-org')
        self.assertEqual(controller.label_variables.count(), 1)
        self.assertEqual(
            controller.label_variables.all()[0].name, 'A_TEST_KEY')
        self.assertEqual(
            controller.label_variables.all()[0].value, 'the value')
        self.assertTrue(controller.slug)

    @responses.activate
    def test_create_new_controller_with_env(self):
        existing_controller = self.mk_controller()

        self.client.login(username='testuser2', password='test')
        self.client.get(
            reverse('organizations:select-active', args=('foo-org',)))

        self.mock_create_marathon_app()

        data = {
            'name': 'Another test app',
            'marathon_cmd': 'ping2',
            'env-0-key': 'A_TEST_KEY',
            'env-0-value': 'the value',
            'env-TOTAL_FORMS': 1,
            'env-INITIAL_FORMS': 0,
            'env-MIN_NUM_FORMS': 0,
            'env-MAX_NUM_FORMS': 100,
            'label-TOTAL_FORMS': 0,
            'label-INITIAL_FORMS': 0,
            'label-MIN_NUM_FORMS': 0,
            'label-MAX_NUM_FORMS': 100,
        }

        response = self.client.post(reverse('base:add'), data)

        self.assertEqual(response.status_code, 302)

        controller = Controller.objects.exclude(
            pk=existing_controller.pk).get()
        self.assertEqual(controller.state, 'done')

        self.assertEqual(controller.name, 'Another test app')
        self.assertEqual(controller.marathon_cmd, 'ping2')
        self.assertEqual(controller.organization.slug, 'foo-org')
        self.assertEqual(controller.env_variables.count(), 1)
        self.assertEqual(controller.env_variables.all()[0].key, 'A_TEST_KEY')
        self.assertEqual(controller.env_variables.all()[0].value, 'the value')
        self.assertTrue(controller.slug)

    @responses.activate
    def test_create_new_controller_error(self):
        self.client.login(username='testuser2', password='test')

        data = {
            'name': 'Another test app',
            'env-TOTAL_FORMS': 1,
            'env-INITIAL_FORMS': 0,
            'env-MIN_NUM_FORMS': 0,
            'env-MAX_NUM_FORMS': 100,
            'label-TOTAL_FORMS': 1,
            'label-INITIAL_FORMS': 0,
            'label-MIN_NUM_FORMS': 0,
            'label-MAX_NUM_FORMS': 100,
        }
        response = self.client.post(reverse('base:add'), data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')
        self.assertEqual(Controller.objects.count(), 0)

        data = {
            'marathon_cmd': 'ping2',
            'env-TOTAL_FORMS': 0,
            'env-INITIAL_FORMS': 0,
            'env-MIN_NUM_FORMS': 0,
            'env-MAX_NUM_FORMS': 100,
            'label-TOTAL_FORMS': 1,
            'label-INITIAL_FORMS': 0,
            'label-MIN_NUM_FORMS': 0,
            'label-MAX_NUM_FORMS': 100,
        }
        response = self.client.post(reverse('base:add'), data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'This field is required')
        self.assertEqual(Controller.objects.count(), 0)

    def test_normal_user_with_no_org_sees_nothing(self):
        controller = self.mk_controller()

        # admin user will see the Test App
        self.client.logout()
        self.client.login(username='testuser2', password='test')
        resp = self.client.get(reverse('home'))
        self.assertContains(resp, 'Test App')

        # normal user with no org will not see the Test App
        User.objects.create_user('joe', 'joe@email.com', '1234')
        self.client.logout()
        self.client.login(username='joe', password='1234')
        resp = self.client.get(reverse('home'))
        self.assertNotContains(resp, 'Test App')

        # normal user with org will see the Test App
        user = User.objects.create_user('joe2', 'joe2@email.com', '1234')
        org = Organization.objects.get(pk=1)
        OrganizationUserRelation.objects.create(user=user, organization=org)
        controller.organization = org
        controller.save()

        self.client.logout()
        self.client.login(username='joe2', password='1234')
        resp = self.client.get(reverse('home'))
        self.assertContains(resp, 'Test App')

    @responses.activate
    def test_advanced_page(self):
        self.client.login(username='testuser2', password='test')
        self.client.get(
            reverse('organizations:select-active', args=('foo-org',)))

        self.mock_create_marathon_app()

        data = {
            'name': 'Another test app',
            'marathon_cmd': 'ping2',
            'env-TOTAL_FORMS': 0,
            'env-INITIAL_FORMS': 0,
            'env-MIN_NUM_FORMS': 0,
            'env-MAX_NUM_FORMS': 100,
            'label-TOTAL_FORMS': 0,
            'label-INITIAL_FORMS': 0,
            'label-MIN_NUM_FORMS': 0,
            'label-MAX_NUM_FORMS': 100,
        }

        response = self.client.post(reverse('base:add'), data)
        self.assertEqual(response.status_code, 302)

        controller = Controller.objects.all().last()
        self.mock_update_marathon_app(controller.app_id)

        self.client.post(
            reverse('base:edit', args=[controller.id]), {
                'name': 'A new name',
                'marathon_cpus': 0.5,
                'marathon_mem': 100.0,
                'marathon_instances': 2,
                'marathon_cmd': '/path/to/exec some command',
                'env-TOTAL_FORMS': 0,
                'env-INITIAL_FORMS': 0,
                'env-MIN_NUM_FORMS': 0,
                'env-MAX_NUM_FORMS': 100,
                'label-TOTAL_FORMS': 0,
                'label-INITIAL_FORMS': 0,
                'label-MIN_NUM_FORMS': 0,
                'label-MAX_NUM_FORMS': 100,
            })
        controller = Controller.objects.get(pk=controller.id)
        self.assertEqual(controller.marathon_cpus, 0.5)
        self.assertEqual(controller.marathon_mem, 100.0)
        self.assertEqual(controller.marathon_instances, 2)
        self.assertEqual(controller.marathon_cmd, '/path/to/exec some command')

    @responses.activate
    def test_advanced_page_marathon_error(self):
        self.client.login(username='testuser2', password='test')
        self.client.get(
            reverse('organizations:select-active', args=('foo-org',)))

        self.mock_create_marathon_app()

        data = {
            'name': 'Another test app',
            'marathon_cmd': 'ping2',
            'env-TOTAL_FORMS': 0,
            'env-INITIAL_FORMS': 0,
            'env-MIN_NUM_FORMS': 0,
            'env-MAX_NUM_FORMS': 100,
            'label-TOTAL_FORMS': 0,
            'label-INITIAL_FORMS': 0,
            'label-MIN_NUM_FORMS': 0,
            'label-MAX_NUM_FORMS': 100,
        }

        response = self.client.post(reverse('base:add'), data)
        self.assertEqual(response.status_code, 302)

        controller = Controller.objects.all().last()
        self.mock_update_marathon_app(controller.app_id, 500)

        self.client.post(
            reverse('base:edit', args=[controller.id]), {
                'name': 'A new name',
                'marathon_cpus': 0.5,
                'marathon_mem': 100.0,
                'marathon_instances': 2,
                'marathon_cmd': '/path/to/exec some command',
                'env-TOTAL_FORMS': 0,
                'env-INITIAL_FORMS': 0,
                'env-MIN_NUM_FORMS': 0,
                'env-MAX_NUM_FORMS': 100,
                'label-TOTAL_FORMS': 0,
                'label-INITIAL_FORMS': 0,
                'label-MIN_NUM_FORMS': 0,
                'label-MAX_NUM_FORMS': 100,
            })
        controller = Controller.objects.get(pk=controller.id)
        self.assertEqual(controller.marathon_cpus, 0.5)
        self.assertEqual(controller.marathon_mem, 100.0)
        self.assertEqual(controller.marathon_instances, 2)
        self.assertEqual(controller.marathon_cmd, '/path/to/exec some command')

        resp = self.client.get(reverse('home'))
        self.assertContains(resp, 'Unable to update controller in marathon')

    def test_view_only_on_homepage(self):
        resp = self.client.get(reverse('home'))
        self.assertNotContains(resp, 'Start new base controller')
        self.assertNotContains(resp, 'edit')

        self.client.login(username='testuser2', password='test')

        self.client.post(
            reverse('user_settings'), {'settings_level': 'expert'})
        resp = self.client.get(reverse('home'))
        self.assertContains(resp, 'Basic')
        self.assertContains(resp, 'Docker')
        self.assertContains(resp, 'card-content new-site')

    def test_staff_access_required(self):
        self.mk_controller(controller={'owner': User.objects.get(pk=2)})

        resp = self.client.get(reverse('base:add'))
        self.assertEqual(resp.status_code, 302)

        resp = self.client.post(reverse('base:add'), {})
        self.assertEqual(resp.status_code, 302)

        resp = self.client.get(reverse('base:edit', args=[1]))
        self.assertEqual(resp.status_code, 302)

    @responses.activate
    def test_applog_view(self):
        self.client.login(username='testuser2', password='test')
        controller = self.mk_controller(controller={
            'owner': User.objects.get(pk=2),
            'state': 'done'})
        setup_responses_for_logdriver(controller)
        response = self.client.get(reverse('base:logs', kwargs={
            'controller_pk': controller.pk,
        }))
        [task] = response.context['tasks']
        self.assertEqual(task['id'], '%s.the-task-id' % (controller.app_id,))
        [task_id] = response.context['task_ids']
        self.assertEqual(task_id, 'the-task-id')

    @responses.activate
    def test_event_source_response_stdout(self):
        self.client.login(username='testuser2', password='test')
        controller = self.mk_controller(controller={
            'owner': User.objects.get(pk=2),
            'state': 'done'})
        setup_responses_for_logdriver(controller)
        resp = self.client.get(reverse('base:logs_event_source', kwargs={
            'controller_pk': controller.pk,
            'task_id': 'the-task-id',
            'path': 'stdout',
        }))
        self.assertEqual(
            resp['X-Accel-Redirect'],
            os.path.join(
                settings.LOGDRIVER_PATH,
                ('worker-machine-1/worker-machine-id'
                 '/frameworks/the-framework-id/executors'
                 '/%s.the-task-id/runs/latest/stdout?n=0' %
                 controller.app_id)))
        self.assertEqual(resp['X-Accel-Buffering'], 'no')

    @responses.activate
    def test_event_source_response_stderr(self):
        self.client.login(username='testuser2', password='test')
        controller = self.mk_controller(controller={
            'owner': User.objects.get(pk=2),
            'state': 'done'})
        setup_responses_for_logdriver(controller)
        resp = self.client.get(reverse('base:logs_event_source', kwargs={
            'controller_pk': controller.pk,
            'task_id': 'the-task-id',
            'path': 'stderr',
        }))
        self.assertEqual(
            resp['X-Accel-Redirect'],
            os.path.join(
                settings.LOGDRIVER_PATH,
                ('worker-machine-1/worker-machine-id'
                 '/frameworks/the-framework-id/executors'
                 '/%s.the-task-id/runs/latest/stderr?n=0' %
                 controller.app_id)))
        self.assertEqual(resp['X-Accel-Buffering'], 'no')

    @responses.activate
    def test_event_source_response_badpath(self):
        self.client.login(username='testuser2', password='test')
        controller = self.mk_controller(controller={
            'owner': User.objects.get(pk=2),
            'state': 'done'})
        setup_responses_for_logdriver(controller)
        # NOTE: bad path according to URL regex, hence the manual requesting
        view = AppEventSourceView()
        request = RequestFactory().get('/')
        request.user = controller.owner
        request.session = {}
        response = view.get(request, controller.pk,
                            'the-task-id', 'foo')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, 'File not found.')

    @responses.activate
    def test_app_restart(self):
        controller = self.mk_controller(controller={
            'owner': User.objects.get(pk=2),
            'state': 'done'})
        self.mock_restart_marathon_app(controller.app_id)

        resp = self.client.get(reverse('base:restart', args=[controller.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(responses.calls), 1)

        resp = self.client.get(reverse('home'))
        self.assertContains(resp, 'App restart sent.')

    @responses.activate
    def test_app_restart_error(self):
        controller = self.mk_controller(controller={
            'owner': User.objects.get(pk=2),
            'state': 'done'})
        self.mock_restart_marathon_app(controller.app_id, 404)

        resp = self.client.get(reverse('base:restart', args=[controller.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(responses.calls), 1)

        resp = self.client.get(reverse('home'))
        self.assertContains(resp, 'App restart failed.')

    @responses.activate
    def test_update_marathon_exists(self):
        self.client.login(username='testuser2', password='test')
        controller = self.mk_controller(controller={
            'owner': User.objects.get(pk=2)})

        self.mock_create_marathon_app()
        controller.get_builder().build()

        self.mock_exists_on_marathon(controller.app_id)
        self.client.get(reverse(
            'base:update_marathon_exists_json', kwargs={
                'controller_pk': controller.pk,
            }))

        controller = Controller.objects.get(pk=controller.pk)
        self.assertEqual(controller.state, 'done')

        # change state to missing
        controller.get_builder().workflow.take_action('missing')
        controller.save()
        controller = Controller.objects.get(pk=controller.pk)
        self.assertEqual(controller.state, 'missing')

        # ensure state is updated after marathon call
        self.client.get(reverse(
            'base:update_marathon_exists_json', kwargs={
                'controller_pk': controller.pk,
            }))

        controller = Controller.objects.get(pk=controller.pk)
        self.assertEqual(controller.state, 'done')

    @responses.activate
    def test_update_marathon_missing(self):
        self.client.login(username='testuser2', password='test')
        controller = self.mk_controller(controller={
            'owner': User.objects.get(pk=2)})

        self.mock_create_marathon_app()
        controller.get_builder().build()

        self.mock_exists_on_marathon(controller.app_id, 404)
        self.client.get(reverse(
            'base:update_marathon_exists_json', kwargs={
                'controller_pk': controller.pk,
            }))

        controller = Controller.objects.get(pk=controller.pk)
        self.assertEqual(controller.state, 'missing')

    @responses.activate
    def test_app_delete(self):
        controller = self.mk_controller(controller={
            'owner': User.objects.get(pk=2),
            'state': 'done'})
        self.mock_delete_marathon_app(controller.app_id)

        self.client.login(username='testuser2', password='test')

        resp = self.client.post(reverse('base:delete', args=[controller.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(responses.calls), 1)

        resp = self.client.get(reverse('home'))
        self.assertContains(resp, 'App deletion sent.')
        self.assertEquals(Controller.objects.all().count(), 0)

    @responses.activate
    def test_app_delete_error(self):
        controller = self.mk_controller(controller={
            'owner': User.objects.get(pk=2),
            'state': 'done'})
        self.mock_delete_marathon_app(controller.app_id, 404)

        self.client.login(username='testuser2', password='test')

        resp = self.client.post(reverse('base:delete', args=[controller.id]))
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(len(responses.calls), 1)

        resp = self.client.get(reverse('home'))
        self.assertContains(resp, 'Failed to delete')
        self.assertEquals(Controller.objects.all().count(), 1)
