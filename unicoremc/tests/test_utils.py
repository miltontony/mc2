import errno

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings

from mock import patch, Mock

from elasticgit.storage import StorageException

from unicoremc.utils import (
    get_hub_app_client, remove_if_exists, git_remove_if_exists)


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

    @patch('unicoremc.utils.os.remove')
    def test_remove_if_exists(self, mocked_remove):
        mocked_remove.side_effect = OSError()
        mocked_remove.side_effect.errno = errno.EPERM
        self.assertRaises(OSError, remove_if_exists, '/')
        mocked_remove.side_effect.errno = errno.ENOENT
        self.assertIs(remove_if_exists('/'), None)

    def test_git_remove_if_exists(self):
        mocked_delete_data = Mock()
        mocked_workspace = Mock(sm=Mock(delete_data=mocked_delete_data))
        mocked_delete_data.side_effect = StorageException(
            'File does not exist')

        self.assertEqual(
            git_remove_if_exists(mocked_workspace, '/', 'foo'), None)
        mocked_delete_data.assert_called_with('/', 'foo')

        mocked_delete_data.side_effect = StorageException(
            'A different error')
        self.assertRaises(
            StorageException, git_remove_if_exists,
            mocked_workspace, '/', 'foo')
