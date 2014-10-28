import os
import json
import responses

from django.contrib.auth.models import User
from django.conf import settings

from git import Repo

from elasticgit.tests.base import ModelBaseTest
from elasticgit.manager import StorageManager


class UnicoremcTestCase(ModelBaseTest):

    def mk_test_repos(self):
        self.user = User.objects.create(
            username='testuser',
            email="test@email.com")

        workdir = os.path.join(settings.CMS_REPO_PATH, 'test-source-repo')
        self.source_repo_sm = StorageManager(Repo.init(workdir))
        self.source_repo_sm.create_storage()
        self.source_repo_sm.write_config('user', {
            'name': 'testuser',
            'email': 'test@email.com',
        })
        self.source_repo_sm.store_data(
            'README.md', 'This is a sample readme', 'Create readme file')
        self.source_repo_sm.store_data(
            'text.txt', 'This is a sample textfile', 'Create sample file')

        workdir = os.path.join(settings.CMS_REPO_PATH, 'test-base-repo')
        self.base_repo_sm = StorageManager(Repo.init(workdir))
        self.base_repo_sm.create_storage()
        self.base_repo_sm.write_config('user', {
            'name': 'testuser',
            'email': 'test@email.com',
        })

        self.base_repo_sm.store_data(
            'sample.txt', 'This is a sample file!', 'Create sample file')

        self.addCleanup(lambda: self.source_repo_sm.destroy_storage())
        self.addCleanup(lambda: self.base_repo_sm.destroy_storage())

    def mock_create_repo(self, status=201, data={}):
        default_response = {
            'clone_url': self.source_repo_sm.repo.git_dir,
            'git_url': self.source_repo_sm.repo.git_dir,
        }
        default_response.update(data)

        responses.add(
            responses.POST, settings.GITHUB_API + 'repos',
            body=json.dumps(default_response),
            content_type="application/json",
            status=status)

    def mock_create_webhook(
            self, status=201, repo='unicore-cms-content-ffl-za'):
        responses.add(
            responses.POST, settings.GITHUB_HOOKS_API % {'repo': repo},
            body=json.dumps({}),
            content_type="application/json",
            status=status)
