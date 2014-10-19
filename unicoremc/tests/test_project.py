import json
import httpretty
import os
import shutil

from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings

from git import Repo

from unicoremc.models import Project
from unicoremc.states import ProjectWorkflow
from unicoremc import exceptions


@httpretty.activate
class ProjectTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='testuser',
            email="test@email.com")

        workdir = os.path.join(settings.CMS_REPO_PATH, 'test-source-repo')
        os.makedirs(workdir)
        self.source_repo = Repo.init(workdir)

    def tearDown(self):
        try:
            shutil.rmtree(self.source_repo.working_dir)
        except:
            pass
        try:
            shutil.rmtree(os.path.join(settings.CMS_REPO_PATH, 'ffl-za'))
        except:
            pass

    def mock_create_repo(self, status=201, data={}):
        default_response = {'clone_url': self.source_repo.git_dir}
        default_response.update(data)

        httpretty.register_uri(
            httpretty.POST,
            settings.GITHUB_API + 'repos',
            body=json.dumps(default_response),
            status=status,
            content_type="application/json")

    def test_create_repo_state(self):
        self.mock_create_repo()

        p = Project(
            app_type='ffl',
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo', access_token='sample-token')

        self.assertEquals(
            p.repo_url,
            self.source_repo.git_dir)
        self.assertEquals(p.state, 'repo_created')

    def test_create_repo_missing_access_token(self):
        self.mock_create_repo()

        p = Project(
            app_type='ffl',
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

        with self.assertRaises(exceptions.AccessTokenRequiredException):
            pw = ProjectWorkflow(instance=p)
            pw.take_action('create_repo')

        self.assertEquals(p.state, 'initial')

    def test_create_repo_bad_response(self):
        self.mock_create_repo(status=404, data={'message': 'Not authorized'})

        p = Project(
            app_type='ffl',
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

        with self.assertRaises(exceptions.GithubApiException):
            pw = ProjectWorkflow(instance=p)
            pw.take_action('create_repo', access_token='sample-token')

        self.assertEquals(p.state, 'initial')

    def test_clone_repo(self):
        self.mock_create_repo()

        p = Project(
            app_type='ffl',
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo', access_token='sample-token')
        pw.take_action('clone_repo')

        self.assertEquals(p.state, 'repo_cloned')
        self.assertTrue(os.path.isdir(os.path.join(p.repo_path(), '.git')))
        shutil.rmtree(p.repo_path())
