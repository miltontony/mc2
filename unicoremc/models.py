import os
import pwd

os.getlogin = lambda: pwd.getpwuid(os.getuid())[0]

import requests

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from unicoremc import constants, exceptions
from unicoremc.manager import ConfigManager, SettingsManager

from git import Repo

from elasticgit.manager import Workspace, StorageManager
from elasticgit import EG
from elasticgit.utils import load_class


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

    def __unicode__(self):
        """
        FIXME: this is probably a bad idea
        """
        language = self.get_code()
        return unicode(
            dict(constants.LANGUAGE_CHOICES).get(language, language))


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
    country = models.CharField(choices=constants.COUNTRY_CHOICES, max_length=2)
    state = models.CharField(max_length=50, default='initial')
    repo_url = models.URLField(blank=True, null=True)
    repo_git_url = models.URLField(blank=True, null=True)
    owner = models.ForeignKey('auth.User')
    team_id = models.IntegerField(blank=True, null=True)
    available_languages = models.ManyToManyField(
        Localisation, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)

        self.config_manager = ConfigManager()
        self.settings_manager = SettingsManager()

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
        repo = Repo(self.repo_path())
        ws = Workspace(repo, None, None)
        ws.fast_forward(remote_name='upstream')

    def push_repo(self):
        repo = Repo(self.repo_path())
        origin = repo.remote(name='origin')
        origin.push()

    def init_workspace(self):
        working_dir = self.repo_path()
        index_prefix = 'unicore_frontend_%(app_type)s_%(country)s' % {
            'app_type': self.app_type,
            'country': self.country.lower(),
        }
        workspace = EG.workspace(working_dir, index_prefix=index_prefix)
        category_model = load_class('unicore.content.models.Category')
        page_model = load_class('unicore.content.models.Page')
        workspace.sync(category_model)
        workspace.sync(page_model)

    def create_supervisor(self):
        self.config_manager.write_frontend_supervisor(
            self.app_type, self.country)

        self.config_manager.write_cms_supervisor(
            self.app_type, self.country)

    def create_nginx(self):
        self.config_manager.write_frontend_nginx(self.app_type, self.country)
        self.config_manager.write_cms_nginx(self.app_type, self.country)

    def create_pyramid_settings(self):
        self.settings_manager.write_frontend_settings(
            self.app_type,
            self.country,
            self.repo_git_url,
            self.available_languages.all(),
            self.frontend_repo_path()
        )

    def create_cms_settings(self):
        self.settings_manager.write_cms_settings(
            self.app_type,
            self.country,
            self.repo_url,
            self.repo_path()
        )
