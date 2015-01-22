import httplib2

from apiclient import discovery
from oauth2client import client


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
        accountId='123456',
        body={
            'websiteUrl': frontend_url,
            'name': name
        }
    ).execute()
    return resp.get("id")
