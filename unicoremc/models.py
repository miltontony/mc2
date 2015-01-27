import shutil
import os
import pwd

os.getlogin = lambda: pwd.getpwuid(os.getuid())[0]

import requests

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from unicoremc import constants, exceptions, mappings
from unicoremc.manager import ConfigManager, SettingsManager, DbManager

from git import Repo

from elasticgit.storage import StorageManager
from elasticgit import EG

from unicore.content.models import (
    Category, Page, Localisation as EGLocalisation)


class Localisation(models.Model):
    """
    Stolen from praekelt/unicore-cms-django.git :: models.Localisation
    """

    country_code = models.CharField(
        _('2 letter country code'), max_length=2,
        help_text=(
            'See http://www.worldatlas.com/aatlas/ctycodes.htm '
            'for reference.'))
    language_code = models.CharField(
        _('3 letter language code'), max_length=3,
        help_text=(
            'See http://www.loc.gov/standards/iso639-2/php/code_list.php '
            'for reference.'))

    @classmethod
    def _for(cls, language):
        language_code, _, country_code = language.partition('_')
        localisation, _ = cls.objects.get_or_create(
            language_code=language_code, country_code=country_code)
        return localisation

    def get_code(self):
        return u'%s_%s' % (self.language_code, self.country_code)

    def get_display_name(self):
        return unicode(constants.LANGUAGES.get(self.language_code))

    def __unicode__(self):
        language = constants.LANGUAGES.get(self.language_code)
        country = constants.COUNTRIES.get(self.country_code)
        return u'%s (%s)' % (language, country)


class Project(models.Model):
    FFL = 'ffl'
    GEM = 'gem'
    EBOLA = 'ebola'
    MAMA = 'mama'
    MNM = 'mnm'
    STRAIGHT_TALK = 'straighttalk'
    BAREFOOT_LAW = 'barefootlaw'
    U_REPORT = 'ureport'
    MARIE_STOPES = 'mariestopes'
    FFL_ANGOLA = 'fflangola'

    APP_TYPES = (
        (FFL, 'Facts for Life'),
        (GEM, 'Girl Effect Mobile'),
        (EBOLA, 'Ebola Information'),
        (MAMA, 'MAMA Baby Center'),
        (MNM, 'Malaria no More'),
        (STRAIGHT_TALK, 'Straight Talk'),
        (BAREFOOT_LAW, 'Barefoot Law'),
        (U_REPORT, 'U-Report'),
        (MARIE_STOPES, 'Marie Stopes'),
        (FFL_ANGOLA, 'FFL Angola'),
    )

    app_type = models.CharField(choices=APP_TYPES, max_length=256)
    base_repo_url = models.URLField()
    country = models.CharField(choices=constants.COUNTRY_CHOICES, max_length=2)
    state = models.CharField(max_length=50, default='initial')
    repo_url = models.URLField(blank=True, null=True)
    repo_git_url = models.URLField(blank=True, null=True)
    owner = models.ForeignKey('auth.User')
    team_id = models.IntegerField(blank=True, null=True)
    project_version = models.PositiveIntegerField(default=0)
    available_languages = models.ManyToManyField(
        Localisation, blank=True, null=True)
    default_language = models.ForeignKey(
        Localisation, blank=True, null=True,
        related_name='default_language')
    ga_profile_id = models.TextField(blank=True, null=True)
    ga_account_id = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('app_type', 'country')

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)

        self.config_manager = ConfigManager()
        self.settings_manager = SettingsManager()
        self.db_manager = DbManager()

    def frontend_url(self):
        return 'http://%(country)s.%(app_type)s.%(env)shub.unicore.io' % {
            'app_type': self.app_type,
            'country': self.country.lower(),
            'env': 'qa-' if settings.DEPLOY_ENVIRONMENT == 'qa' else ''
        }

    def cms_url(self):
        return 'http://cms.%(country)s.%(app_type)s.%(env)shub.unicore.io' % {
            'app_type': self.app_type,
            'country': self.country.lower(),
            'env': 'qa-' if settings.DEPLOY_ENVIRONMENT == 'qa' else ''
        }

    def repo_path(self):
        repo_folder_name = '%(app_type)s-%(country)s' % {
            'app_type': self.app_type,
            'country': self.country.lower()
        }
        return os.path.join(settings.CMS_REPO_PATH, repo_folder_name)

    def frontend_repo_path(self):
        repo_folder_name = '%(app_type)s-%(country)s' % {
            'app_type': self.app_type,
            'country': self.country.lower()
        }
        return os.path.join(settings.FRONTEND_REPO_PATH, repo_folder_name)

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
            "has_issues": True,
            "auto_init": True,
            "team_id": self.team_id,
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
            self.repo_git_url = resp.json().get('git_url')
            self.save()
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

        # Github creates a README.md when initializing a repo
        # We need to remove this to avoid conflicts
        readme_path = os.path.join(self.repo_path(), 'README.md')
        if os.path.exists(readme_path):
            repo.index.remove([readme_path])
            repo.index.commit('remove initial readme')
            os.remove(readme_path)

    def create_remote(self):
        repo = Repo(self.repo_path())
        repo.create_remote('upstream', self.base_repo_url)

    def merge_remote(self):
        index_prefix = 'unicore_cms_%(app_type)s_%(country)s' % {
            'app_type': self.app_type,
            'country': self.country.lower(),
        }

        workspace = self.setup_workspace(self.repo_path(), index_prefix)
        workspace.fast_forward(remote_name='upstream')

    def push_repo(self):
        repo = Repo(self.repo_path())
        origin = repo.remote(name='origin')
        origin.push()

    def setup_workspace(self, repo_path, index_prefix):
        workspace = EG.workspace(repo_path, index_prefix=index_prefix)

        branch = workspace.sm.repo.active_branch
        if workspace.im.index_exists(branch.name):
            workspace.im.destroy_index(branch.name)

        workspace.setup(self.owner.username, self.owner.email)

        while not workspace.index_ready():
            pass

        workspace.setup_custom_mapping(Category, mappings.CategoryMapping)
        workspace.setup_custom_mapping(Page, mappings.PageMapping)
        workspace.setup_custom_mapping(EGLocalisation,
                                       mappings.LocalisationMapping)
        return workspace

    def sync_cms_index(self):
        index_prefix = 'unicore_cms_%(app_type)s_%(country)s' % {
            'app_type': self.app_type,
            'country': self.country.lower(),
        }

        workspace = EG.workspace(self.repo_path(), index_prefix=index_prefix)
        workspace.sync(Category)
        workspace.sync(Page)
        workspace.sync(EGLocalisation)

    def sync_frontend_index(self):
        index_prefix = 'unicore_frontend_%(app_type)s_%(country)s' % {
            'app_type': self.app_type,
            'country': self.country.lower(),
        }

        ws = self.setup_workspace(self.frontend_repo_path(), index_prefix)
        ws.sync(Category)
        ws.sync(Page)
        ws.sync(EGLocalisation)

    def init_workspace(self):
        self.sync_cms_index()

        # We also need to clone the repo for the frontend and initialize it
        Repo.clone_from(self.repo_git_url, self.frontend_repo_path())
        self.sync_frontend_index()

    def create_nginx(self):
        self.config_manager.write_frontend_nginx(self.app_type, self.country)
        self.config_manager.write_cms_nginx(self.app_type, self.country)

    def create_pyramid_settings(self):
        self.settings_manager.write_frontend_settings(
            self.app_type,
            self.country,
            self.repo_git_url,
            self.available_languages.all(),
            self.frontend_repo_path(),
            self.default_language or Localisation._for('eng_GB'),
            self.ga_profile_id
        )

    def create_cms_settings(self):
        self.settings_manager.write_cms_settings(
            self.app_type,
            self.country,
            self.repo_url,
            self.repo_path()
        )
        self.settings_manager.write_cms_config(
            self.app_type,
            self.country,
            self.repo_url,
            self.repo_path()
        )

    def create_webhook(self, access_token):
        repo_name = constants.NEW_REPO_NAME_FORMAT % {
            'app_type': self.app_type,
            'country': self.country.lower(),
            'suffix': settings.GITHUB_REPO_NAME_SUFFIX}

        post_data = {
            "name": "web",
            "active": True,
            "events": ["push"],
            "config": {
                "url": "%s/api/notify/" % self.frontend_url(),
                "content_type": "json"
            }
        }

        if access_token:
            headers = {'Authorization': 'token %s' % access_token}
            resp = requests.post(
                settings.GITHUB_HOOKS_API % {'repo': repo_name},
                json=post_data,
                headers=headers)

            if resp.status_code != 201:
                raise exceptions.GithubApiException(
                    'Create hooks failed with response: %s - %s' %
                    (resp.status_code, resp.json().get('message')))
        else:
            raise exceptions.AccessTokenRequiredException(
                'access_token is required')

    def create_db(self):
        self.db_manager.create_db(self.app_type, self.country)

    def init_db(self):
        self.db_manager.init_db(self.app_type, self.country)

    def destroy(self):
        shutil.rmtree(self.repo_path())
        shutil.rmtree(self.frontend_repo_path())
        self.config_manager.destroy(self.app_type, self.country)
        self.settings_manager.destroy(self.app_type, self.country)
        self.db_manager.destroy(self.app_type, self.country)
