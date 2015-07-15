import os
import json
import responses
import shutil
import uuid
from urlparse import urljoin

from django.test import TransactionTestCase
from django.conf import settings

from git import Repo
import mock

from elasticgit.tests.base import ModelBaseTest
from elasticgit.storage import StorageManager

from unicore.hub.client import App

from unicoremc.managers import NginxManager, SettingsManager
from unicoremc.models import Project, ProjectRepo, AppType
from unicore.content.models import (
    Category, Page, Localisation as EGLocalisation)


class UnicoremcTestCase(TransactionTestCase, ModelBaseTest):

    def get_nginx_manager(self):
        nm = NginxManager()
        self.addCleanup(lambda: [shutil.rmtree(dir_) for dir_ in nm.dirs])
        return nm

    def get_settings_manager(self):
        sm = SettingsManager()
        self.addCleanup(lambda: [shutil.rmtree(dir_) for dir_ in sm.dirs])
        return sm

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

    def mk_hub_app(self, **fields):
        data = {
            'title': 'Foo',
            'url': 'http://localhost/foo',
            'uuid': uuid.uuid4().hex,
            'key': 'anapikey'
        }
        data.update(fields)
        return App(mock.Mock(), data)

    def mk_project(self, app_type={}, repo={}, project={}):
        app_type_defaults = {
            'name': 'ffl',
            'title': 'Facts for Life',
            'project_type': 'unicore-cms'
        }
        app_type_defaults.update(app_type)
        app_type = AppType._for(**app_type_defaults)

        project_defaults = {
            'owner': getattr(self, 'user', None),
            'country': 'ZA',
            'application_type': app_type
        }
        project_defaults.update(project)
        project = Project.objects.create(**project_defaults)

        repo_defaults = {
            'project': project,
            'base_url': 'http://some-git-repo.com'
        }
        repo_defaults.update(repo)
        ProjectRepo.objects.create(**repo_defaults)

        return project

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

    def mock_list_repos(self, data=[]):
        responses.add(
            responses.GET, settings.GITHUB_API +
            'repos?type=public&per_page=100&page=1',
            body=json.dumps(data),
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

    def mock_create_unicore_distribute_repo(self, status=200):
        responses.add(
            responses.POST, '%s/repos.json' % settings.UNICORE_DISTRIBUTE_HOST,
            body=json.dumps({}),
            content_type="application/json",
            status=status)

    def mock_create_marathon_app(self, status=201):
        responses.add(
            responses.POST, '%s/v2/apps' % settings.MESOS_MARATHON_HOST,
            body=json.dumps({}),
            content_type="application/json",
            status=status)

    def mock_update_marathon_app(self, app_type, country, app_id, status=200):
        responses.add(
            responses.PUT, '%s/v2/apps/%s-%s-%s' % (
                settings.MESOS_MARATHON_HOST, app_type, country, app_id),
            body=json.dumps({}),
            content_type="application/json",
            status=status)

    def mock_create_hub_app(self, **fields):

        def make_response(request):
            data = json.loads(request.body)
            data.update({
                'uuid': uuid.uuid4().hex,
                'key': 'anapikey'
            })
            data.update(fields)
            return (201, {}, json.dumps(data))

        responses.add_callback(
            responses.POST,
            urljoin(settings.HUBCLIENT_SETTINGS['host'], 'apps'),
            callback=make_response,
            content_type="application/json")

    def mock_create_all(self):
        self.mock_create_repo()
        self.mock_create_webhook()
        self.mock_create_hub_app()
        self.mock_create_unicore_distribute_repo()
        self.mock_create_marathon_app()
