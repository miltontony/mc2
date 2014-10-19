import json
import httpretty

from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings

from unicoremc.models import Project
from unicoremc.states import (
    ProjectWorkflow, GithubApiException, AccessTokenRequiredException)


@httpretty.activate
class ProjectTestCase(TestCase):
    DEFAULT_RESPONSE = {
        'clone_url': ('http://new-git-repo/user/'
                      'unicore-cms-content-ffl-za.git'),
    }

    def setUp(self):
        self.user = User.objects.create(
            username='testuser',
            email="test@email.com")

    def mock_create_repo(self, status=201, data=DEFAULT_RESPONSE):
        httpretty.register_uri(
            httpretty.POST,
            settings.GITHUB_API + 'repos',
            body=json.dumps(data),
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
            'http://new-git-repo/user/unicore-cms-content-ffl-za.git')
        self.assertEquals(p.state, 'repo_created')

    def test_create_repo_missing_access_token(self):
        self.mock_create_repo()

        p = Project(
            app_type='ffl',
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

        with self.assertRaises(AccessTokenRequiredException):
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

        with self.assertRaises(GithubApiException):
            pw = ProjectWorkflow(instance=p)
            pw.take_action('create_repo', access_token='sample-token')

        self.assertEquals(p.state, 'initial')
