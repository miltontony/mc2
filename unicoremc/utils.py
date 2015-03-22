import httplib2

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from apiclient import discovery
from oauth2client import client

from unicore.hub.client import AppClient


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
