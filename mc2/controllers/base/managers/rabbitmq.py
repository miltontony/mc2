import base64
import hashlib
import random
import time
import uuid

from django.conf import settings

from pyrabbit.api import Client
from pyrabbit.http import HTTPError


class ControllerRabbitMQManager(object):

    def __init__(self, controller):
        """
        A helper manager to get to connect to RabbitMQ

        :param controller Controller: A Controller model instance
        """
        self.ctrl = controller
        self.client = Client(
            settings.RABBITMQ_API_HOST,
            settings.RABBITMQ_API_USERNAME,
            settings.RABBITMQ_API_PASSWORD)
        print self.client

    def _create_password(self):
        # Guranteed random dice rolls
        return base64.b64encode(
            hashlib.sha1(uuid.uuid1().hex).hexdigest())[:24]

    def _create_username(self):
        return base64.b64encode(str(
            time.time() + random.random() * time.time())).strip('=').lower()

    def create_rabbitmq_vhost(self):
        """
        Attempts to create a new vhost. Returns false if vhost already exists.
        The new username/password will be saved on the controller if a new
        vhost was created

        :returns: bool
        """
        try:
            self.client.get_vhost(self.ctrl.rabbitmq_vhost_name)
            return False  # already exists
        except HTTPError:
            pass

        self.client.create_vhost(self.ctrl.rabbitmq_vhost_name)
        # create user/pass
        username = self._create_username()
        password = self._create_password()

        self.client.create_user(username, password)

        # save newly created username/pass
        self.ctrl.rabbitmq_vhost_username = username
        self.ctrl.rabbitmq_vhost_password = password
        self.ctrl.rabbitmq_vhost_host = settings.RABBITMQ_APP_HOST
        self.ctrl.save()

        self.client.set_vhost_permissions(
            self.ctrl.rabbitmq_vhost_name, username, '.*', '.*', '.*')
        return True
