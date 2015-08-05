import os
import errno
import httplib2
from urlparse import urljoin

import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.cache import cache

from apiclient import discovery
from oauth2client import client

from elasticgit.storage import StorageException

from unicore.hub.client import AppClient
from unicoremc import constants


def remove_if_exists(path):
    """
    Removes file and fails silently if file does not exist.
    """
    try:
        os.remove(path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


def git_remove_if_exists(workspace, path, commit_msg):
    """
    Removes file from repo and fails silently if file does not exist.
    """
    try:
        workspace.sm.delete_data(path, commit_msg)
    except StorageException as e:
        if 'does not exist' not in e.message:
            raise


def get_ga_accounts(access_token):
    credentials = client.AccessTokenCredentials(
        access_token,
        'unicore-hub/1.0')
    http = credentials.authorize(http=httplib2.Http())
    service = discovery.build('analytics', 'v3', http=http)
    resp = service.management().accounts().list().execute()
    return resp.get('items', [])


def create_ga_profile(access_token, account_id, frontend_url, name):
    credentials = client.AccessTokenCredentials(
        access_token,
        'unicore-hub/1.0')
    http = credentials.authorize(http=httplib2.Http())
    service = discovery.build('analytics', 'v3', http=http)

    resp = service.management().webproperties().insert(
        accountId=account_id,
        body={
            'websiteUrl': frontend_url,
            'name': name
        }
    ).execute()

    profile_id = resp.get("id")
    create_ga_default_view(access_token, account_id, profile_id)
    return profile_id


def create_ga_default_view(access_token, account_id, profile_id):
    credentials = client.AccessTokenCredentials(
        access_token,
        'unicore-hub/1.0')
    http = credentials.authorize(http=httplib2.Http())
    service = discovery.build('analytics', 'v3', http=http)

    resp = service.management().profiles().insert(
        accountId=account_id,
        webPropertyId=profile_id,
        body={
            'name': 'All Web Site Data'
        }
    ).execute()
    return resp.get("id")


def get_hub_app_client():
    """
    Returns an instance of AppClient if settings are present, otherwise
    returns None. Raises ImproperlyConfigured if the settings are invalid.
    """
    client_settings = getattr(settings, 'HUBCLIENT_SETTINGS', None)
    if client_settings is None:
        return None

    try:
        client = AppClient(**client_settings)
        return client
    except KeyError as e:
        raise ImproperlyConfigured('%s is missing in HUBCLIENT_SETTINGS' % e)


def get_default_docker_cmd(application_type, country):
    docker_cmd = ''
    if application_type:
        if application_type.project_type == 'springboard':
            ini = os.path.join(
                '/var/unicore-configs/',
                'springboard_settings/%s_%s.ini' % (
                    application_type.name,
                    country.lower())
                )
            docker_cmd = constants.MARATHON_CMD % {
                'config_path': ini}

        elif application_type.project_type == 'unicore-cms':
            ini = os.path.join(
                '/var/unicore-configs/',
                'frontend_settings/%s_%s.ini' % (
                    application_type.name,
                    country.lower())
                )
            docker_cmd = constants.MARATHON_CMD % {
                'config_path': ini}
    return docker_cmd


def get_repos(refresh):
    """
    Fetches and returns a list of public repos from Github. Caches
    the result.
    """
    if not refresh:
        return cache.get('repos')
    url = urljoin(
        settings.GITHUB_API, 'repos?type=public&per_page=100&page=%s')
    pageNum = 1
    repos = []
    while True:
        response = requests.get(url % pageNum)
        data = response.json()
        if not data:
            break
        repos.extend(data)
        pageNum += 1
    repos = [{
        'name': r.get('name'),
        'git_url': r.get('git_url'),
        'clone_url': r.get('clone_url')
    } for r in repos]
    cache.set('repos', repos)
    return repos


def get_teams():
    """
    Fetches and returns a list of organization teams from Github. Caches
    the result.
    """
    teams = cache.get('teams')
    if teams is not None:
        return teams

    url = urljoin(
        settings.GITHUB_API, 'teams')
    response = requests.get(
        url, auth=(settings.GITHUB_USERNAME, settings.GITHUB_TOKEN))
    teams = response.json()
    cache.set('teams', teams, timeout=60*30)
    return teams
