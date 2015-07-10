import shutil
import os
import pwd
import functools

os.getlogin = lambda: pwd.getpwuid(os.getuid())[0]  # noqa

import requests

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from unicoremc import constants, exceptions, mappings
from unicoremc.managers import NginxManager, SettingsManager, DbManager

from git import Repo

from elasticgit.storage import StorageManager
from elasticgit import EG

from unicore.content.models import (
    Category, Page, Localisation as EGLocalisation)

from unicoremc.utils import get_hub_app_client
from unicoremc.exceptions import ProjectNotStandaloneException


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

    class Meta:
        ordering = ('language_code', )


class AppType(models.Model):
    UNICORE_CMS = 'unicore-cms'
    SPRINGBOARD = 'springboard'
    PROJECT_TYPES = (
        (UNICORE_CMS, 'unicore-cms'),
        (SPRINGBOARD, 'springboard'),
    )

    name = models.CharField(max_length=256, blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    project_type = models.CharField(
        choices=PROJECT_TYPES, max_length=256, default=UNICORE_CMS)

    @classmethod
    def _for(cls, name, title, project_type):
        application_type, _ = cls.objects.get_or_create(
            name=name, title=title, project_type=project_type)
        return application_type

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.project_type)

    class Meta:
        ordering = ('title', )


class ProjectRepo(models.Model):
    project = models.ForeignKey('Project', related_name='repos')
    base_url = models.URLField()
    git_url = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)


class ProjectManager(models.Manager):
    '''
    Custom manager that uses prefetch_related and select_related
    for repos and application_type to improve performance.
    '''
    def get_queryset(self):
        qs = super(ProjectManager, self).get_queryset()
        return qs.select_related('application_type').prefetch_related('repos')


def standalone_only(method):
    '''
    A decorator for Project methods that should only be executed
    when the project is standalone.
    '''
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.is_standalone():
            return method(self, *args, **kwargs)
        raise ProjectNotStandaloneException(
            '%s was called for a non-standalone project' % (method.__name__,))
    return wrapper


class Project(models.Model):
    objects = ProjectManager()

    application_type = models.ForeignKey(AppType, blank=True, null=True)
    country = models.CharField(
        choices=constants.COUNTRY_CHOICES, max_length=256)
    state = models.CharField(max_length=50, default='initial')
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
    frontend_custom_domain = models.TextField(
        blank=True, null=True, default='')
    cms_custom_domain = models.TextField(
        blank=True, null=True, default='')
    hub_app_id = models.CharField(blank=True, null=True, max_length=32)

    class Meta:
        ordering = ('application_type__title', 'country')

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)

        self.nginx_manager = NginxManager()
        self.settings_manager = SettingsManager()
        self.db_manager = DbManager()

    @property
    def app_type(self):
        if self.application_type:
            return self.application_type.name
        return ''

    def _get_repo_attribute(self, attr):
        repos = self.repos.all()
        return [getattr(repo, attr) for repo in repos]

    def base_repo_urls(self):
        return self._get_repo_attribute('base_url')

    def repo_urls(self):
        return self._get_repo_attribute('url')

    def repo_git_urls(self):
        return self._get_repo_attribute('git_url')

    def is_standalone(self):
        '''
        Returns True if the project needs its own repo, index and CMS.
        This is only False if the project has more than one base repo.
        '''
        return self.repos.count() <= 1

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

    def hub_app_title(self):
        return '%s - %s' % (
            self.application_type.title, self.get_country_display())

    def hub_app(self):
        if self.hub_app_id is None:
            return None

        if not getattr(self, '_hub_app', None):
            client = get_hub_app_client()
            if client is None:
                return None
            self._hub_app = client.get_app(self.hub_app_id)

        return self._hub_app

    def create_or_update_hub_app(self):
        client = get_hub_app_client()
        if client is None:
            return None

        if self.hub_app_id:
            app = client.get_app(self.hub_app_id)
            app.set('title', self.hub_app_title())
            app.set('url', self.frontend_url())
            app.save()
        else:
            app = client.create_app({
                'title': self.hub_app_title(),
                'url': self.frontend_url()
            })
            self.hub_app_id = app.get('uuid')
            self.save()

        self._hub_app = app
        return app

    @standalone_only
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

            repo_db = self.repos.all()[0]
            repo_db.url = resp.json().get('clone_url')
            repo_db.git_url = resp.json().get('git_url')
            repo_db.save()
        else:
            raise exceptions.AccessTokenRequiredException(
                'access_token is required')

    @standalone_only
    def clone_repo(self):
        repo = Repo.clone_from(self.repo_urls()[0], self.repo_path())
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

    @standalone_only
    def create_remote(self):
        repo = Repo(self.repo_path())
        repo.create_remote('upstream', self.base_repo_urls()[0])

    @standalone_only
    def merge_remote(self):
        index_prefix = 'unicore_cms_%(app_type)s_%(country)s' % {
            'app_type': self.app_type,
            'country': self.country.lower(),
        }

        workspace = self.setup_workspace(self.repo_path(), index_prefix)
        workspace.fast_forward(remote_name='upstream')

    @standalone_only
    def push_repo(self):
        repo = Repo(self.repo_path())
        origin = repo.remote(name='origin')
        origin.push()

    @standalone_only
    def setup_workspace(self, repo_path, index_prefix):
        workspace = EG.workspace(
            repo_path, index_prefix=index_prefix,
            es={'urls': settings.ELASTICSEARCH_HOST})

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

    @standalone_only
    def sync_cms_index(self):
        index_prefix = 'unicore_cms_%(app_type)s_%(country)s' % {
            'app_type': self.app_type,
            'country': self.country.lower(),
        }

        workspace = EG.workspace(
            self.repo_path(), index_prefix=index_prefix,
            es={'urls': settings.ELASTICSEARCH_HOST})
        workspace.sync(Category)
        workspace.sync(Page)
        workspace.sync(EGLocalisation)

    @standalone_only
    def sync_frontend_index(self):
        index_prefix = 'unicore_frontend_%(app_type)s_%(country)s' % {
            'app_type': self.app_type,
            'country': self.country.lower(),
        }

        ws = self.setup_workspace(self.frontend_repo_path(), index_prefix)
        ws.sync(Category)
        ws.sync(Page)
        ws.sync(EGLocalisation)

    @standalone_only
    def init_workspace(self):
        self.sync_cms_index()
        self.create_unicore_distribute_repo()

    def create_nginx(self):
        self.nginx_manager.write_frontend_nginx(
            self.app_type, self.country, self.frontend_custom_domain)
        self.nginx_manager.write_cms_nginx(
            self.app_type, self.country, self.cms_custom_domain)

    def create_pyramid_settings(self):
        if self.application_type.project_type == AppType.UNICORE_CMS:
            self.settings_manager.write_frontend_settings(
                self.app_type,
                self.country,
                self.available_languages.all(),
                self.default_language or Localisation._for('eng_GB'),
                self.ga_profile_id,
                self.hub_app()
            )
        elif self.application_type.project_type == AppType.SPRINGBOARD:
            self.settings_manager.write_springboard_settings(
                self.app_type,
                self.country,
                self.available_languages.all(),
                self.default_language or Localisation._for('eng_GB'),
                self.ga_profile_id,
                self.hub_app()
            )
        else:
            raise exceptions.ProjecTyeRequiredException(
                'project_type is required')

    @standalone_only
    def create_cms_settings(self):
        self.settings_manager.write_cms_settings(
            self.app_type,
            self.country,
            self.repo_urls()[0],
            self.repo_path()
        )
        self.settings_manager.write_cms_config(
            self.app_type,
            self.country,
            self.repo_urls()[0],
            self.repo_path()
        )

    @standalone_only
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

    @standalone_only
    def create_unicore_distribute_repo(self):
        post_data = {
            "repo_url": self.repo_git_urls()[0]
        }

        resp = requests.post(
            '%s/repos.json' % settings.UNICORE_DISTRIBUTE_HOST,
            json=post_data)

        if resp.status_code != 200:
            raise exceptions.UnicoreDistributeApiException(
                'Clone repo failed with response: %s - %s' %
                (resp.status_code, resp.json().get('errors')))

    @standalone_only
    def create_db(self):
        self.db_manager.create_db(self.app_type, self.country)

    @standalone_only
    def init_db(self):
        self.db_manager.init_db(self.app_type, self.country)

    def create_marathon_app(self):
        if self.application_type.project_type == AppType.SPRINGBOARD:
            cmd = constants.SPRINGBOARD_MARATHON_CMD % {
                'config_path': os.path.join(
                    settings.UNICORE_CONFIGS_INSTALL_DIR,
                    self.settings_manager.get_springboard_settings_path(
                        self.app_type, self.country.lower())
                    ),
            }
            self.initiate_create_marathon_app(cmd)
        elif self.application_type.project_type == AppType.UNICORE_CMS:
            cmd = constants.UNICORECMS_MARATHON_CMD % {
                'config_path': os.path.join(
                    settings.UNICORE_CONFIGS_INSTALL_DIR,
                    self.settings_manager.get_frontend_settings_path(
                        self.app_type, self.country.lower())
                    ),
            }
            self.initiate_create_marathon_app(cmd)

    def initiate_create_marathon_app(self, cmd):
        post_data = {
            "id": "%(app_type)s-%(country)s-%(id)s" % {
                'app_type': self.app_type,
                'country': self.country.lower(),
                'id': self.id,
            },
            "cmd": cmd,
            "cpus": 0.1,
            "mem": 100.0,
            "instances": 1
        }

        resp = requests.post(
            '%s/v2/apps' % settings.MESOS_MARATHON_HOST,
            json=post_data)

        if resp.status_code != 201:
            raise exceptions.MarathonApiException(
                'Create Marathon app failed with response: %s - %s' %
                (resp.status_code, resp.json().get('message')))

    def destroy(self):
        shutil.rmtree(self.repo_path())
        self.nginx_manager.destroy(self.app_type, self.country)
        self.settings_manager.destroy(self.app_type, self.country)

        if self.application_type.project_type == AppType.UNICORE_CMS:
            self.settings_manager.destroy_unicore_cms_settings(
                self.app_type, self.country)

        if self.application_type.project_type == AppType.SPRINGBOARD:
            self.settings_manager.destroy_springboard_settings(
                self.app_type, self.country)

        self.db_manager.destroy(self.app_type, self.country)
