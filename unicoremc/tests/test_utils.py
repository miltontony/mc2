import os
import json
import errno

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.cache import get_cache
from django.test.utils import override_settings

import responses
from mock import patch, Mock

from elasticgit.storage import StorageException

from unicoremc.tests.base import UnicoremcTestCase
from unicoremc.utils import (
    get_hub_app_client, remove_if_exists, git_remove_if_exists,
    get_repos, get_teams)


class UtilsTestCase(UnicoremcTestCase):

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

    @responses.activate
    def test_get_repos(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        test_repos_path = os.path.join(cur_dir, 'repos.json')

        with open(test_repos_path, "r") as repos_file:
            data = repos_file.read()
        repos = json.loads(data)

        self.mock_list_repos(repos)

        with patch(
                'unicoremc.utils.cache',
                new=get_cache('django.core.cache.backends.locmem.LocMemCache')
                ):
            data = get_repos(refresh=True)
            self.assertEquals(
                data[0], {
                    'clone_url':
                        'https://github.com/universalcore/unicore-cms.git',
                    'git_url': 'git://github.com/universalcore/unicore-cms.git',
                    'name': 'unicore-cms'}
            )
            self.assertTrue(get_repos())
            self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_get_repos_no_repos(self):
        self.mock_list_repos()
        data = get_repos()
        self.assertIs(data, None)

    @responses.activate
    def test_get_teams(self):
        self.mock_get_teams()
        with patch(
                'unicoremc.utils.cache',
                new=get_cache('django.core.cache.backends.locmem.LocMemCache')
                ):
            data = get_teams()
            self.assertEqual(data[0]['slug'], 'foo')
            data = get_teams()
            self.assertEqual(data[0]['slug'], 'foo')

        self.assertEqual(len(responses.calls), 1)
        self.assertIn('Authorization', responses.calls[0].request.headers)
