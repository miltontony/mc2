import json
import httpretty
import os
import shutil

from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from django.test.client import RequestFactory

from git import Repo
from elasticgit.manager import StorageManager

from unicoremc.models import Project
from unicoremc.views import start_new_project


@httpretty.activate
class ViewsTestCase(TestCase):

    def setUp(self):
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

        workdir = os.path.join(settings.CMS_REPO_PATH, 'test-base-repo')
        self.base_repo_sm = StorageManager(Repo.init(workdir))
        self.base_repo_sm.create_storage()
        self.base_repo_sm.write_config('user', {
            'name': 'testuser',
            'email': 'test@email.com',
        })

        self.base_repo_sm.store_data(
            'sample.txt', 'This is a sample file!', 'Create sample file')

    def tearDown(self):
        self.source_repo_sm.destroy_storage()
        self.base_repo_sm.destroy_storage()

        try:
            # TODO: Use `pw.take_action('destory')` to cleanup
            shutil.rmtree(os.path.join(settings.CMS_REPO_PATH, 'ffl-za'))
        except:
            pass

    def mock_create_repo(self, status=201, data={}):
        default_response = {'clone_url': self.source_repo_sm.repo.git_dir}
        default_response.update(data)

        httpretty.register_uri(
            httpretty.POST,
            settings.GITHUB_API + 'repos',
            body=json.dumps(default_response),
            status=status,
            content_type="application/json")

    def test_create_new_project(self):
        self.mock_create_repo()
        data = {
            'app_type': 'ffl',
            'base_repo': self.base_repo_sm.repo.git_dir,
            'country': 'ZA',
            'access_token': 'some-access-token',
            'user_id': self.user.id,
            'team_id': 1
        }
        request = RequestFactory().post('/new/create/', data)
        response = start_new_project(request)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(json.loads(response.content), {
            'success': True
        })

        project = Project.objects.all()[0]
        self.assertEqual(project.state, 'done')
