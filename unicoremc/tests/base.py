import os
import json
import responses
import shutil

from django.test import TransactionTestCase
from django.conf import settings

from git import Repo

from elasticgit.tests.base import ModelBaseTest
from elasticgit.storage import StorageManager

from unicoremc.managers import NginxManager
from unicore.content.models import (
    Category, Page, Localisation as EGLocalisation)


class UnicoremcTestCase(TransactionTestCase, ModelBaseTest):

    def get_nginx_manager(self):
        nm = NginxManager()
        self.addCleanup(lambda: [shutil.rmtree(dir_) for dir_ in nm.dirs])
        return nm

    def mk_test_repos(self):
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

        remote_workspace = self.mk_workspace(
            working_dir=settings.CMS_REPO_PATH,
            name='test-base-repo',
            index_prefix='%s_remote' % (self.mk_index_prefix(),))

        remote_workspace.setup('Test Kees', 'kees@example.org')
        remote_workspace.setup_mapping(Category)
        remote_workspace.setup_mapping(Page)
        remote_workspace.setup_mapping(EGLocalisation)

        cat = Category({
            'title': 'Some title',
            'slug': 'some-slug'
        })
        remote_workspace.save(cat, 'Saving a Category')

        page = Page({
            'title': 'Some page title',
            'slug': 'some-page-slug'
        })
        remote_workspace.save(page, 'Saving a Page')

        loc = EGLocalisation({
            'locale': 'spa_ES',
            'image': 'some-image-uuid',
            'image_host': 'http://some.site.com',
        })
        remote_workspace.save(loc, 'Saving a Localisation')
        remote_workspace.refresh_index()

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

    def mock_list_repos(self):
        default_response = [{
            'clone_url': '',
            'git_url': '',
        }]
        responses.add(
            responses.GET, settings.GITHUB_API +
            'repos?type=public&per_page=100&page=1',
            body=json.dumps(default_response),
            content_type="application/json",
            status=200,
            match_querystring=True)
        responses.add(
            responses.GET, settings.GITHUB_API +
            'repos?type=public&per_page=100&page=2',
            body=json.dumps([]),
            content_type="application/json",
            status=200,
            match_querystring=True)

    def mock_create_webhook(
            self, status=201, repo='unicore-cms-content-ffl-za'):
        responses.add(
            responses.POST, settings.GITHUB_HOOKS_API % {'repo': repo},
            body=json.dumps({}),
            content_type="application/json",
            status=status)
