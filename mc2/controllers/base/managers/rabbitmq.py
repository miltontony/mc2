import base64
import hashlib
import json
import random
import requests
import time
import urllib
import uuid

from django.conf import settings


class ControllerRabbitMQManager(object):

    def __init__(self, controller):
        """
        A helper manager to get to connect to RabbitMQ

        :param controller Controller: A Controller model instance
        """
        self.ctrl = controller
        self.auth = requests.auth.HTTPBasicAuth(
            settings.RABBITMQ_API_USERNAME, settings.RABBITMQ_API_PASSWORD)

    def _do_call(self, method, url, data=None, headers=None, timeout=5):
        req_headers = {'Content-Type': 'application/json'}

        if headers:
            req_headers.update(headers)

        response = requests.request(
            method, url, data=data, headers=req_headers,
            auth=self.auth,
            timeout=timeout)
        response.raise_for_status()
        return response

    def _create_password(self):
        # Guranteed random dice rolls
        return base64.b64encode(
            hashlib.sha1(uuid.uuid1().hex).hexdigest())[:24]

    def _create_username(self, vhost_name):
        random_name = base64.b64encode(str(
            time.time() + random.random() * time.time())).strip('=').lower()
        return '%s_%s' % (vhost_name, random_name)

    def _get_vhost(self, vhost_name):
        response = self._do_call('GET', '%s/vhosts/%s' % (
            settings.RABBITMQ_API_HOST,
            vhost_name))
        return response.json().get('name')

    def _create_vhost(self, vhost_name):
        response = self._do_call('PUT', '%s/vhosts/%s' % (
            settings.RABBITMQ_API_HOST, vhost_name))
        return response

    def _get_user(self, username):
        response = self._do_call('GET', '%s/users/%s' % (
            settings.RABBITMQ_API_HOST,
            username))
        return response.json().get('name')

    def _create_user(self, username, password, tags="management"):
        response = self._do_call('PUT', '%s/users/%s' % (
            settings.RABBITMQ_API_HOST, username),
            data=json.dumps({'password': password, 'tags': tags}))
        return response

    def _set_vhost_permissions(
            self, vhost_name, username, cfg=".*", wr=".*", rd=".*"):
        response = self._do_call('PUT', '%s/permissions/%s/%s' % (
            settings.RABBITMQ_API_HOST, vhost_name, username),
            data=json.dumps({"configure": cfg, "write": wr, "read": rd}))
        return response

    def create_rabbitmq_vhost(self):
        """
        Attempts to create a new vhost. Returns false if vhost already exists.
        The new username/password will be saved on the controller if a new
        vhost was created

        :returns: bool
        """
        vhost_name = urllib.quote(self.ctrl.rabbitmq_vhost_name)

        try:
            self._get_vhost(vhost_name)
            return False  # already exists
        except requests.exceptions.HTTPError:
            pass

        self._create_vhost(vhost_name)

        # create user/pass
        username = self.ctrl.rabbitmq_vhost_username or \
            self._create_username(vhost_name)
        password = self._create_password()

        try:
            self._get_user(username)
            return False  # already exists
        except requests.exceptions.HTTPError:
            self._create_user(username, password)

        # save newly created username/pass
        self.ctrl.rabbitmq_vhost_username = username
        self.ctrl.rabbitmq_vhost_password = password
        self.ctrl.rabbitmq_vhost_host = settings.RABBITMQ_APP_HOST
        self.ctrl.save()

        self._set_vhost_permissions(vhost_name, username)
        return True
