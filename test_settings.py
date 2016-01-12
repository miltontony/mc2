from mc2.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mc2_test.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

DEBUG = True
CELERY_ALWAYS_EAGER = True


def scratchpath(*paths):
    return abspath('.scratchpath', *paths)

SCRATCHPATH = scratchpath()

UNICORE_CMS_INSTALL_DIR = scratchpath('test_config_dir', 'unicore-cms-django')
UNICORE_CMS_PYTHON_VENV = '/path/to/bin/python'
UNICORE_CONFIGS_INSTALL_DIR = '/path/to/unicore-configs'

REPO_WORKSPACE = 'test_repo_dir'
FRONTEND_REPO_PATH = scratchpath(REPO_WORKSPACE, 'frontend')
CMS_REPO_PATH = scratchpath(REPO_WORKSPACE, 'cms')

CONFIG_WORKSPACE = 'test_config_dir'
CONFIGS_REPO_PATH = scratchpath('test_config_repo_dir')
NGINX_CONFIGS_PATH = scratchpath(CONFIGS_REPO_PATH, 'nginx')
SPRINGBOARD_SETTINGS_OUTPUT_PATH = scratchpath(
    CONFIGS_REPO_PATH, 'springboard_settings')
FRONTEND_SETTINGS_OUTPUT_PATH = scratchpath(
    CONFIGS_REPO_PATH, 'frontend_settings')
CMS_SETTINGS_OUTPUT_PATH = scratchpath(CONFIG_WORKSPACE, 'cms_settings')

FRONTEND_SOCKETS_PATH = scratchpath('test_sockets_dir', 'frontend_sockets')
CMS_SOCKETS_PATH = scratchpath('test_sockets_dir', 'cms_sockets')

RAVEN_DSN_FRONTEND_QA = 'raven-qa'
RAVEN_DSN_FRONTEND_PROD = 'raven-prod'

RAVEN_DSN_CMS_QA = 'raven-cms-qa'
RAVEN_DSN_CMS_PROD = 'raven-cms-prod'

ELASTICSEARCH_HOST = 'http://localhost:9200'
UNICORE_DISTRIBUTE_HOST = 'http://testserver:6543'
MESOS_MARATHON_HOST = 'http://testserver:8080'
LOGDRIVER_PATH = '/logdriver-testing/'
MESOS_HTTP_PORT = 5555

THUMBOR_SECURITY_KEY = 'some-key'

HUBCLIENT_SETTINGS = {
    'host': 'http://testserver:8888',
    'app_id': '',
    'app_key': '',
    'redirect_to_https': False,
}
