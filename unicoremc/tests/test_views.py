import json
import os
import shutil
import pytest
import responses

from django.contrib.auth.models import User
from django.conf import settings
from django.test.client import RequestFactory

from git import Repo
from elasticgit.manager import StorageManager

from unicoremc.models import Project
from unicoremc.views import start_new_project

from unicore.content.models import Category, Page
from unicoremc.tests.base import UnicoremcTestCase


@pytest.mark.django_db
class ViewsTestCase(UnicoremcTestCase):

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

    @responses.activate
    def test_create_new_project(self):
        self.mock_create_repo()

        self.workspace = self.mk_workspace()
        self.workspace.setup('Test Kees', 'kees@example.org')
        self.workspace.setup_mapping(Category)
        self.workspace.setup_mapping(Page)

        cat = Category({
            'title': 'Some title',
            'slug': 'some-slug'
        })
        self.workspace.save(cat, 'Saving a Category')

        page = Page({
            'title': 'Some page title',
            'slug': 'some-page-slug'
        })
        self.workspace.save(page, 'Saving a Page')

        self.workspace.refresh_index()
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
