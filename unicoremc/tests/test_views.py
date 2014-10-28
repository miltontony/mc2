import json
import httpretty
import os
import shutil
import pytest

from unittest import skip

from django.contrib.auth.models import User
from django.conf import settings
from django.test.client import RequestFactory

from git import Repo
from elasticgit.manager import StorageManager
from elasticgit.tests.base import ModelBaseTest

from unicoremc.models import Project
from unicoremc.views import start_new_project

from unicore.content.models import Category, Page


@pytest.mark.django_db
@httpretty.activate
class ViewsTestCase(ModelBaseTest):

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

        self.addCleanup(self.source_repo_sm.destroy_storage)
        self.addCleanup(self.base_repo_sm.destroy_storage)

        self.addCleanup(httpretty.disable)
        self.addCleanup(httpretty.reset)

    def mock_create_repo(self, status=201, data={}):
        default_response = {'clone_url': self.source_repo_sm.repo.git_dir}
        default_response.update(data)

        httpretty.register_uri(
            httpretty.POST,
            settings.GITHUB_API + 'repos',
            body=json.dumps(default_response),
            status=status,
            content_type="application/json")

    @skip("currently failing")
    def test_create_new_project(self):
        self.workspace = self.mk_workspace()
        self.workspace.setup('Test Kees', 'kees@example.org')
        self.workspace.setup_mapping(Category)
        self.workspace.setup_mapping(Page)

        cat = Category({
            'title': 'Some title',
            'slug': 'some-slug'
        })
        workspace.save(cat, 'Saving a Category')

        page = Page({
            'title': 'Some page title',
            'slug': 'some-page-slug'
        })
        workspace.save(page, 'Saving a Page')

        workspace.refresh_index()

        self.mock_create_repo()
        data = {
            'app_type': 'ffl',
            'base_repo': self.base_repo_sm.repo.git_dir,
            'country': 'ZA',
            'access_token': 'some-access-token',
            'user_id': self.user.id
        }
        request = RequestFactory().post('/new/create/', data)
        response = start_new_project(request)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(json.loads(response.content), {
            'success': True
        })

        project = Project.objects.all()[0]
        self.assertEqual(project.state, 'done')

        self.addCleanup(lambda: shutil.rmtree(
            os.path.join(settings.CMS_REPO_PATH, 'ffl-za')))
