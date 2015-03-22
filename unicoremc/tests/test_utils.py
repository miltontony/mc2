from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings

from unicoremc.utils import get_hub_app_client


class UtilsTestCase(TestCase):

    @override_settings(HUBCLIENT_SETTINGS={})
    def test_get_hub_app_client(self):
        # no settings
        del settings.HUBCLIENT_SETTINGS
        self.assertEqual(get_hub_app_client(), None)

        # incomplete settings
        with self.settings(HUBCLIENT_SETTINGS={
                'app_id': '1234',
                'app_key': '1234'}):
            with self.assertRaisesRegexp(
                    ImproperlyConfigured, "'host' is missing"):
                get_hub_app_client()

        # complete settings
        with self.settings(HUBCLIENT_SETTINGS={
                'host': 'http://localhost/',
                'app_id': '1234',
                'app_key': '1234'}):
            client = get_hub_app_client()
            self.assertTrue(client)
