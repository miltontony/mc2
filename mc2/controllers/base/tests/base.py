import json
import responses

from django.test import TransactionTestCase
from django.conf import settings

from mc2.controllers.base.models import Controller, EnvVariable, MarathonLabel


class ControllerBaseTestCase(TransactionTestCase):

    def mk_controller(self, controller={}):
        controller_defaults = {
            'owner': getattr(self, 'user', None),
            'name': 'Test App',
            'marathon_cmd': 'ping'
        }

        controller_defaults.update(controller)
        return Controller.objects.create(**controller_defaults)

    def mk_labels_variable(self, controller, **env):
        env_defaults = {
            'controller': controller,
            'name': 'TEST_LABELS_NAME',
            'value': 'a test label value'
        }

        env_defaults.update(env)
        return MarathonLabel.objects.create(**env_defaults)

    def mk_env_variable(self, controller, **env):
        env_defaults = {
            'controller': controller,
            'key': 'TEST_KEY',
            'value': 'a test value'
        }

        env_defaults.update(env)
        return EnvVariable.objects.create(**env_defaults)

    def mock_create_marathon_app(self, status=201):
        responses.add(
            responses.POST, '%s/v2/apps' % settings.MESOS_MARATHON_HOST,
            body=json.dumps({}),
            content_type="application/json",
            status=status)

    def mock_create_postgres_db(self, status=200, data={}):
        responses.add(
            responses.POST, '%s/queues/postgres/wait/create_database'
            % settings.SEED_XYLEM_API_HOST,
            body=json.dumps(data),
            content_type="application/json",
            status=status)

    def mock_update_marathon_app(self, app_id, status=200):
        responses.add(
            responses.PUT, '%s/v2/apps/%s' % (
                settings.MESOS_MARATHON_HOST, app_id),
            body=json.dumps({}),
            content_type="application/json",
            status=status)

    def mock_restart_marathon_app(self, app_id, status=200):
        responses.add(
            responses.POST, '%s/v2/apps/%s/restart' % (
                settings.MESOS_MARATHON_HOST, app_id),
            body=json.dumps({}),
            content_type="application/json",
            status=status)

    def mock_delete_marathon_app(self, app_id, status=200):
        responses.add(
            responses.DELETE, '%s/v2/apps/%s' % (
                settings.MESOS_MARATHON_HOST, app_id),
            body=json.dumps({}),
            content_type="application/json",
            status=status)

    def mock_exists_on_marathon(self, app_id, status=200):
        responses.add(
            responses.GET, '%s/v2/apps/%s' % (
                settings.MESOS_MARATHON_HOST, app_id),
            body=json.dumps({}),
            content_type="application/json",
            status=status)

    def mock_get_vhost(self, vhost_name, status=200):
        responses.add(
            responses.GET, '%s/vhosts/%s' % (
                settings.RABBITMQ_API_HOST, vhost_name),
            body=json.dumps({'name': vhost_name}),
            content_type="application/json",
            status=status)

    def mock_put_vhost(self, vhost_name, status=204):
        responses.add(
            responses.PUT, '%s/vhosts/%s' % (
                settings.RABBITMQ_API_HOST, vhost_name),
            body=json.dumps({}),
            content_type="application/json",
            status=status)

    def mock_get_user(self, name, status=200):
        responses.add(
            responses.GET, '%s/users/%s' % (
                settings.RABBITMQ_API_HOST, name),
            body=json.dumps({'name': name}),
            content_type="application/json",
            status=status)

    def mock_put_user(self, name, status=200):
        responses.add(
            responses.PUT, '%s/users/%s' % (
                settings.RABBITMQ_API_HOST, name),
            body=json.dumps({}),
            content_type="application/json",
            status=status)

    def mock_put_vhost_permissions(self, vhost, username, status=200):
        responses.add(
            responses.PUT, '%s/permissions/%s/%s' % (
                settings.RABBITMQ_API_HOST, vhost, username),
            body=json.dumps({}),
            content_type="application/json",
            status=status)

    def mock_successful_new_vhost(self, vhost_name, vhost_user):
        self.mock_get_vhost(vhost_name, status=404)
        self.mock_put_vhost(vhost_name)
        self.mock_get_user(vhost_user, status=404)
        self.mock_put_user(vhost_user)
        self.mock_put_vhost_permissions(vhost_name, vhost_user)
