import shutil
import os
import pwd
import json
from urlparse import urljoin

os.getlogin = lambda: pwd.getpwuid(os.getuid())[0]  # noqa

import requests

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

from unicoremc import constants, exceptions, mappings
from unicoremc.managers import NginxManager, SettingsManager, DbManager
from unicoremc.websites.managers import (
    UnicoreCmsWebsiteManager, SpringboardWebsiteManager,
    AggregatorWebsiteManager)

from git import Repo

from elasticgit.storage import StorageManager
from elasticgit import EG

from unicore.content.models import (
    Category, Page, Localisation as EGLocalisation)

from unicoremc.utils import get_hub_app_client

from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage


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
    docker_image = models.CharField(max_length=256, blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    project_type = models.CharField(
        choices=PROJECT_TYPES, max_length=256, default=UNICORE_CMS)

    def to_dict(self):
        return {
            'name': self.name,
            'title': self.title,
            'docker_image': self.docker_image,
            'project_type': self.project_type
        }

    def get_qualified_name(self):
        return "%(project_type)s-%(app_type)s" % {
            'project_type': self.project_type,
            'app_type': self.name
        }

    @classmethod
    def _for(cls, name, title, project_type, docker_image):
        application_type, _ = cls.objects.get_or_create(
            name=name,
            title=title,
            project_type=project_type,
            docker_image=docker_image)
        return application_type

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.project_type)

    class Meta:
        ordering = ('title', )


class ProjectRepo(models.Model):
    project = models.OneToOneField(
        'Project', primary_key=True, related_name='repo')
    base_url = models.URLField()
    git_url = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    def __unicode__(self):
        return os.path.basename(self.url) if self.url else None

    def name(self):
        return constants.NEW_REPO_NAME_FORMAT % {
            'app_type': self.project.app_type,
            'country': self.project.country.lower(),
            'suffix': settings.GITHUB_REPO_NAME_SUFFIX}


class ProjectManager(models.Manager):
    '''
    Custom manager that uses prefetch_related and select_related
    for repos and application_type to improve performance.
    '''
    def get_queryset(self):
        qs = super(ProjectManager, self).get_queryset()
        return (qs
                .select_related('application_type', 'repo', 'organization')
                .prefetch_related('external_repos'))


class Project(models.Model):
    objects = ProjectManager()

    application_type = models.ForeignKey(AppType, blank=True, null=True)
    country = models.CharField(
        choices=constants.COUNTRY_CHOICES, max_length=256)
    external_repos = models.ManyToManyField(
        ProjectRepo, blank=True, null=True, related_name='external_projects')
    state = models.CharField(max_length=50, default='initial')
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
    marathon_cpus = models.FloatField(
        default=settings.MESOS_DEFAULT_CPU_SHARE)
    marathon_mem = models.FloatField(
        default=settings.MESOS_DEFAULT_MEMORY_ALLOCATION)
    marathon_instances = models.IntegerField(
        default=settings.MESOS_DEFAULT_INSTANCES)
    marathon_health_check_path = models.CharField(
        max_length=255, blank=True, null=True)
    docker_cmd = models.TextField(blank=True, null=True)

    # Ownership and auth fields
    owner = models.ForeignKey('auth.User')
    team_id = models.IntegerField(blank=True, null=True)
    organization = models.ForeignKey(
        'organizations.Organization', blank=True, null=True)

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

    @property
    def app_id(self):
        return "%(app_type)s-%(country)s-%(id)s" % {
            'app_type': self.app_type,
            'country': self.country.lower(),
            'id': self.id,
        }

    def own_repo(self):
        try:
            return self.repo
        except ProjectRepo.DoesNotExist:
            return None

    def all_repos(self):
        external_repos = list(self.external_repos.all())
        own_repo = self.own_repo()
        if own_repo:
            return [own_repo] + external_repos
        return external_repos

    def get_state_display(self):
        return self.get_website_manager().workflow.get_state()

    def get_generic_domain(self):
        hub = 'qa-hub' if settings.DEPLOY_ENVIRONMENT == 'qa' else 'hub'
        return '%(app_id)s.%(hub)s.unicore.io' % {
            'app_id': self.app_id,
            'hub': hub
        }

    def get_country_domain(self):
        hub = 'qa-hub' if settings.DEPLOY_ENVIRONMENT == 'qa' else 'hub'
        return "%(country)s.%(app_type)s.%(hub)s.unicore.io" % {
            'country': self.country.lower(),
            'app_type': self.app_type,
            'hub': hub
        }

    def to_dict(self):
        return {
            'id': self.id,
            'app_id': self.app_id,
            'app_type': self.app_type,
            'application_type': self.application_type.to_dict()
            if self.application_type else None,
            'base_repo_urls': [r.base_url for r in self.all_repos()],
            'country': self.country,
            'country_display': self.get_country_display(),
            'state': self.state,
            'state_display': self.get_state_display(),
            'repo_urls': [r.url for r in self.all_repos()],
            'repo_git_urls': [r.git_url for r in self.all_repos()],
            'team_id': self.team_id,
            'available_languages': [
                lang.get_code() for lang in self.available_languages.all()],
            'default_language': self.default_language.get_code()
            if self.default_language else None,
            'ga_profile_id': self.ga_profile_id or '',
            'ga_account_id': self.ga_account_id or '',
            'frontend_custom_domain': self.frontend_custom_domain or '',
            'cms_custom_domain': self.cms_custom_domain or '',
            'hub_app_id': self.hub_app_id or '',
            'docker_cmd': self.docker_cmd or '',
        }

    def get_website_manager(self):
        if not (self.application_type and self.application_type.project_type):
            raise exceptions.ProjectTypeRequiredException(
                'project_type is required')

        if not self.own_repo():
            return AggregatorWebsiteManager(self)

        if self.application_type.project_type == AppType.UNICORE_CMS:
            return UnicoreCmsWebsiteManager(self)

        if self.application_type.project_type == AppType.SPRINGBOARD:
            return SpringboardWebsiteManager(self)

        raise exceptions.ProjectTypeUnknownException(
            'project_type is unknown')

    def frontend_url(self):
        return 'http://%s' % self.get_generic_domain()

    def cms_url(self):
        return 'http://cms.%s' % self.get_generic_domain()

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

    def create_repo(self):
        repo_db = self.own_repo()
        new_repo_name = repo_db.name()

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

        resp = requests.post(
            urljoin(settings.GITHUB_API, 'repos'),
            json=post_data,
            auth=(settings.GITHUB_USERNAME, settings.GITHUB_TOKEN))

        if resp.status_code != 201:
            raise exceptions.GithubApiException(
                'Create repo failed with response: %s - %s' %
                (resp.status_code, resp.json().get('message')))

        repo_db.url = resp.json().get('clone_url')
        repo_db.git_url = resp.json().get('git_url')
        repo_db.save()

    def clone_repo(self):
        repo = Repo.clone_from(self.own_repo().url, self.repo_path())
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
        repo.create_remote('upstream', self.own_repo().base_url)

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
        self.create_unicore_distribute_repo()

    def create_nginx(self):
        domain = 'cms.%s %s' % (
            self.get_generic_domain(), self.cms_custom_domain)
        self.nginx_manager.write_cms_nginx(
            self.app_type, self.country, domain.strip())

    def create_pyramid_settings(self):
        if self.application_type.project_type == AppType.UNICORE_CMS:
            self.settings_manager.write_frontend_settings(
                self.app_type,
                self.country,
                self.available_languages.all(),
                self.default_language or Localisation._for('eng_GB'),
                self.ga_profile_id,
                self.hub_app(),
                self.all_repos()[0].name()
            )
        elif self.application_type.project_type == AppType.SPRINGBOARD:
            self.settings_manager.write_springboard_settings(
                self.app_type,
                self.country,
                self.available_languages.all(),
                self.default_language or Localisation._for('eng_GB'),
                self.ga_profile_id,
                self.hub_app(),
                [repo.name() for repo in self.all_repos()]
            )
        else:
            raise exceptions.ProjectTypeRequiredException(
                'project_type is required')

    def create_cms_settings(self):
        self.settings_manager.write_cms_settings(
            self.app_type,
            self.country,
            self.own_repo().url,
            self.repo_path()
        )
        self.settings_manager.write_cms_config(
            self.app_type,
            self.country,
            self.own_repo().url,
            self.repo_path()
        )

    def create_webhook(self):
        repo_name = self.own_repo().name()

        post_data = {
            "name": "web",
            "active": True,
            "events": ["push"],
            "config": {
                "url": "%s/api/notify/" % self.frontend_url(),
                "content_type": "json"
            }
        }

        resp = requests.post(
            settings.GITHUB_HOOKS_API % {'repo': repo_name},
            json=post_data,
            auth=(settings.GITHUB_USERNAME, settings.GITHUB_TOKEN))

        if resp.status_code != 201:
            raise exceptions.GithubApiException(
                'Create hooks failed with response: %s - %s' %
                (resp.status_code, resp.json().get('message')))

    def create_unicore_distribute_repo(self):
        post_data = {
            "repo_url": self.own_repo().git_url
        }

        resp = requests.post(
            '%s/repos.json' % settings.UNICORE_DISTRIBUTE_HOST,
            json=post_data)

        if resp.status_code != 200:
            raise exceptions.UnicoreDistributeApiException(
                'Clone repo failed with response: %s - %s' %
                (resp.status_code, resp.json().get('errors')))

    def create_db(self):
        self.db_manager.create_db(self.app_type, self.country)

    def init_db(self):
        self.db_manager.init_db(
            self.app_type, self.country, push_to_git=True)

    def create_marathon_app(self):
        self.initiate_create_marathon_app()

    def get_marathon_app_data(self):
        if not (self.application_type and self.application_type.project_type):
            raise exceptions.ProjectTypeRequiredException(
                'project_type is required')

        domain = "%(generic_domain)s %(custom)s" % {
            'generic_domain': self.get_generic_domain(),
            'custom': self.frontend_custom_domain
        }

        app_data = {
            "id": self.app_id,
            "cmd": self.docker_cmd,
            "cpus": self.marathon_cpus,
            "mem": self.marathon_mem,
            "instances": self.marathon_instances,
            "labels": {
                "domain": domain.strip(),
                "country": self.get_country_display(),
                "project_type": self.application_type.project_type
            },
            "container": {
                "type": "DOCKER",
                "docker": {
                    "image": self.application_type.docker_image,
                    "forcePullImage": True,
                    "network": "BRIDGE",
                    "portMappings": [{"containerPort": 5656, "hostPort": 0}],
                    "parameters": [{
                        "key": "add-host",
                        "value": "servicehost:%s" % settings.SERVICE_HOST_IP}]
                },
                "volumes": [{
                    "containerPath": "/var/unicore-configs",
                    "hostPath": settings.UNICORE_CONFIGS_INSTALL_DIR,
                    "mode": "RO"
                }]
            }
        }

        if self.marathon_health_check_path:
            app_data.update({
                "ports": [0],
                "healthChecks": [{
                    "gracePeriodSeconds": 3,
                    "intervalSeconds": 10,
                    "maxConsecutiveFailures": 3,
                    "path": self.marathon_health_check_path,
                    "portIndex": 0,
                    "protocol": "HTTP",
                    "timeoutSeconds": 5
                }]
            })

        return app_data

    def initiate_create_marathon_app(self):
        post_data = self.get_marathon_app_data()
        resp = requests.post(
            '%s/v2/apps' % settings.MESOS_MARATHON_HOST,
            json=post_data)

        if resp.status_code != 201:
            raise exceptions.MarathonApiException(
                'Create Marathon app failed with response: %s - %s' %
                (resp.status_code, resp.json().get('message')))

    def update_marathon_app(self):
        post_data = self.get_marathon_app_data()
        app_id = post_data.pop('id')
        resp = requests.put(
            '%(host)s/v2/apps/%(id)s' % {
                'host': settings.MESOS_MARATHON_HOST,
                'id': app_id
            },
            json=post_data)

        if resp.status_code not in [200, 201]:
            raise exceptions.MarathonApiException(
                'Update Marathon app failed with response: %s - %s' %
                (resp.status_code, resp.json().get('message')))

    def destroy(self):
        shutil.rmtree(self.repo_path(), ignore_errors=True)
        self.nginx_manager.destroy(self.app_type, self.country)
        self.settings_manager.destroy(self.app_type, self.country)

        if self.application_type.project_type == AppType.UNICORE_CMS:
            self.settings_manager.destroy_unicore_cms_settings(
                self.app_type, self.country)

        if self.application_type.project_type == AppType.SPRINGBOARD:
            self.settings_manager.destroy_springboard_settings(
                self.app_type, self.country)

        self.db_manager.destroy(self.app_type, self.country)


@receiver(post_save, sender=Project)
def publish_to_websocket(sender, instance, created, **kwargs):
    '''
    Broadcasts the state of a project when it is saved.
    broadcast channel: progress
    '''
    # TODO: apply permissions here?
    data = instance.to_dict()
    data.update({'is_created': created})
    redis_publisher = RedisPublisher(facility='progress', broadcast=True)
    message = RedisMessage(json.dumps(data))
    redis_publisher.publish_message(message)
