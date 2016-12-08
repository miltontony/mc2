import requests

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from polymorphic.models import PolymorphicModel

from mc2.controllers.base import exceptions, namers
from mc2.controllers.base.builders import Builder
from mc2.controllers.base.managers import ControllerInfrastructureManager


class Controller(PolymorphicModel):
    # state
    marathon_cpus = models.FloatField(
        default=settings.MESOS_DEFAULT_CPU_SHARE)
    marathon_mem = models.FloatField(
        default=settings.MESOS_DEFAULT_MEMORY_ALLOCATION)
    marathon_instances = models.IntegerField(
        default=settings.MESOS_DEFAULT_INSTANCES)
    marathon_cmd = models.TextField(default='', blank=True, null=True)

    name = models.TextField(
        help_text='A descriptive name to uniquely identify a controller')
    description = models.TextField(
        help_text='A description to provide more info about a controller',
        blank=True, null=True, default='')
    slug = models.SlugField(
        max_length=255,
        db_index=True,
        help_text='Unique name for use in marathon id',
    )
    state = models.CharField(max_length=50, default='initial')

    # create postgres databases through mission control
    postgres_db_needed = models.BooleanField(default=False)
    postgres_db_name = models.TextField(default='', blank=True, null=True)
    postgres_db_host = models.TextField(default='', blank=True, null=True)
    postgres_db_username = models.TextField(default='', blank=True, null=True)
    postgres_db_password = models.TextField(default='', blank=True, null=True)

    # Ownership and auth fields
    owner = models.ForeignKey('auth.User')
    team_id = models.IntegerField(blank=True, null=True)
    organization = models.ForeignKey(
        'organizations.Organization', blank=True, null=True)

    created_at = models.DateTimeField(
        _('Created Date & Time'),
        db_index=True,
        auto_now_add=True,
        help_text=_(
            'Date and time on which this item was created. This is'
            'automatically set on creation')
    )
    modified_at = models.DateTimeField(
        _('Modified Date & Time'),
        db_index=True,
        editable=False,
        auto_now=True,
        help_text=_(
            'Date and time on which this item was last modified. This'
            'is automatically set each time the item is saved.')
    )

    webhook_token = models.UUIDField(null=True)

    class Meta:
        ordering = ('name', )

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)

        self.infra_manager = ControllerInfrastructureManager(self)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = namers.do_me_a_unique_slug(self.__class__, 'slug')
        super(Controller, self).save(*args, **kwargs)

    def get_state_display(self):
        return self.get_builder().workflow.get_state()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'app_id': self.app_id,
            'state': self.state,
            'state_display': self.get_state_display(),
            'marathon_cmd': self.marathon_cmd,
        }

    @property
    def app_id(self):
        """
        The app id to use for marathon
        """
        return self.slug

    def get_builder(self):
        return Builder(self)

    def get_or_create_postgres_db(self):
        resp = requests.post(
            '%s/queues/postgres/wait/create_database'
            % settings.SEED_XYLEM_API_HOST, json={
                'name': self.app_id.replace('-', '_')})

        if resp.status_code != 200:
            raise exceptions.XylemApiException(
                'Create Postgres DB app failed with response: %s - %s' %
                (resp.status_code, resp.json().get('result', {}).get('Err')))

        result = resp.json().get('result')
        if not result:
            raise exceptions.XylemApiException('Invalid response from api.')

        db_username = result.get('username') or result.get('user')
        db_host = result.get('host') or result.get('hostname')

        self.postgres_db_name = result.get('name')
        self.postgres_db_username = db_username
        self.postgres_db_password = result.get('password')
        self.postgres_db_host = db_host
        self.save()

    def get_default_app_labels(self):
        return {
            "name": self.name,
            "org": self.organization.slug if self.organization else '',
        }

    def get_marathon_app_data(self):
        """
        Override this method to specify the app definition sent to marathon
        """
        data = {
            "id": self.app_id,
            "cpus": self.marathon_cpus,
            "mem": self.marathon_mem,
            "instances": self.marathon_instances,
        }

        if self.marathon_cmd:
            data.update({"cmd": self.marathon_cmd})

        envs = {}
        if self.env_variables.exists():
            envs = dict([
                (env.key, env.value)
                for env in self.env_variables.all()])

        if self.postgres_db_needed:
            self.get_or_create_postgres_db()
            envs.update({
                'DATABASE_URL': 'postgres://%(username)s:'
                '%(password)s@%(host)s/%(name)s' % {
                    'username': self.postgres_db_username,
                    'password': self.postgres_db_password,
                    'host': self.postgres_db_host,
                    'name': self.postgres_db_name,
                }})
        else:
            self.postgres_db_username = None
            self.postgres_db_password = None
            self.postgres_db_host = None
            self.postgres_db_name = None
            self.save()

            # TODO: seed-xylem currently doesn't support deleting of databases
            # Once support is added, we should delete this database here.

        if envs:
            data.update({'env': envs})

        service_labels = self.get_default_app_labels()

        # Update custom labels
        if self.label_variables.exists():
            for label in self.label_variables.all():
                service_labels[label.name] = label.value

        data.update({'labels': service_labels})

        return data

    def create_marathon_app(self):
        post_data = self.get_marathon_app_data()
        resp = requests.post(
            '%s/v2/apps' % settings.MESOS_MARATHON_HOST,
            json=post_data)

        if resp.status_code != 201:
            raise exceptions.MarathonApiException(
                'Create Marathon app failed with response: %s - %s' %
                (resp.status_code, resp.json().get('message')))

    def update_marathon_app(self):
        post_data = self.get_marathon_app_data()
        app_id = post_data.pop('id')
        resp = requests.put(
            '%(host)s/v2/apps/%(id)s' % {
                'host': settings.MESOS_MARATHON_HOST,
                'id': app_id
            },
            json=post_data)

        if resp.status_code not in [200, 201]:
            raise exceptions.MarathonApiException(
                'Update Marathon app failed with response: %s - %s' %
                (resp.status_code, resp.json().get('message')))

    def marathon_restart_app(self):
        resp = requests.post(
            '%(host)s/v2/apps/%(id)s/restart' % {
                'host': settings.MESOS_MARATHON_HOST,
                'id': self.app_id
            },
            json={})

        if resp.status_code != 200:
            raise exceptions.MarathonApiException(
                'Restart Marathon app failed with response: %s - %s' %
                (resp.status_code, resp.json().get('message')))

    def marathon_destroy_app(self):
        resp = requests.delete(
            '%(host)s/v2/apps/%(id)s' % {
                'host': settings.MESOS_MARATHON_HOST,
                'id': self.app_id
            },
            json={})

        if resp.status_code != 200:
            raise exceptions.MarathonApiException(
                'Marathon app deletion failed with response: %s - %s' %
                (resp.status_code, resp.json().get('message')))

    def exists_on_marathon(self):
        resp = requests.get(
            '%(host)s/v2/apps/%(id)s' % {
                'host': settings.MESOS_MARATHON_HOST,
                'id': self.app_id
            },
            json={})
        return resp.status_code == 200

    def destroy(self):
        """
        TODO: destoy running marathon instance
        """
        pass


class EnvVariable(models.Model):
    controller = models.ForeignKey(Controller, related_name='env_variables')
    key = models.TextField(blank=True, null=False)
    value = models.TextField(blank=True, null=True)


class MarathonLabel(models.Model):
    controller = models.ForeignKey(Controller, related_name='label_variables')
    name = models.TextField(blank=True, null=False)
    value = models.TextField(blank=True, null=True)


class AdditionalLink(models.Model):
    controller = models.ForeignKey(Controller, related_name='additional_link')
    name = models.TextField(blank=True, null=False)
    link = models.TextField(blank=True, null=True)
