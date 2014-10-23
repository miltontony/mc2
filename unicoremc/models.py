import os
import requests

from django.db import models
from django.conf import settings

from unicoremc import constants, exceptions
from unicoremc.manager import ConfigManager

from git import Repo
from elasticgit.manager import Workspace, StorageManager


class Project(models.Model):
    FFL = 'ffl'
    GEM = 'gem'
    EBOLA = 'ebola'
    MAMA = 'mama'

    APP_TYPES = (
        (FFL, 'Facts for Life'),
        (GEM, 'Girl Effect Mobile'),
        (EBOLA, 'Ebola Information'),
        (MAMA, 'MAMA Baby Center')
    )

    app_type = models.CharField(choices=APP_TYPES, max_length=10)
    base_repo_url = models.URLField()
    country = models.CharField(choices=constants.COUNTRIES, max_length=2)
    state = models.CharField(max_length=50, default='initial')
    repo_url = models.URLField(blank=True, null=True)
    owner = models.ForeignKey('auth.User')

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)

        self.config_manager = ConfigManager()

    def repo_path(self):
        repo_folder_name = '%(app_type)s-%(country)s' % {
            'app_type': self.app_type,
            'country': self.country.lower()
        }
        return os.path.join(settings.CMS_REPO_PATH, repo_folder_name)

    def create_repo(self, access_token):
        new_repo_name = constants.NEW_REPO_NAME_FORMAT % {
            'app_type': self.app_type,
            'country': self.country.lower(),
            'suffix': settings.GITHUB_REPO_NAME_SUFFIX}

        post_data = {
            "name": new_repo_name,
            "description": "A Unicore CMS content repo for %s %s" % (
                self.app_type, self.country),
            "homepage": "https://github.com",
            "private": False,
            "has_issues": True
        }

        if access_token:
            headers = {'Authorization': 'token %s' % access_token}
            resp = requests.post(
                settings.GITHUB_API + 'repos',
                json=post_data,
                headers=headers)

            if resp.status_code != 201:
                raise exceptions.GithubApiException(
                    'Create repo failed with response: %s - %s' %
                    (resp.status_code, resp.json().get('message')))

            self.repo_url = resp.json().get('clone_url')
        else:
            raise exceptions.AccessTokenRequiredException(
                'access_token is required')

    def clone_repo(self):
        repo = Repo.clone_from(self.repo_url, self.repo_path())
        sm = StorageManager(repo)
        sm.create_storage()
        sm.write_config('user', {
            'name': self.owner.username,
            'email': self.owner.email,
        })

    def create_remote(self):
        repo = Repo(self.repo_path())
        repo.create_remote('upstream', self.base_repo_url)

    def merge_remote(self):
        repo = Repo(self.repo_path())
        ws = Workspace(repo, None, None)
        ws.fast_forward(remote_name='upstream')

    def create_supervisor(self):
        self.config_manager.write_frontend_supervisor(
            self.app_type, self.country)

        self.config_manager.write_cms_supervisor(
            self.app_type, self.country)

    def create_nginx(self):
        self.config_manager.write_frontend_nginx(self.app_type, self.country)
        self.config_manager.write_cms_nginx(self.app_type, self.country)
