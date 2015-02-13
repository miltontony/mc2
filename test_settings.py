from project.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'unicore_mc.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

DEBUG = True
CELERY_ALWAYS_EAGER = True

UNICORE_CMS_INSTALL_DIR = abspath('.test_config_dir', 'unicore-cms-django')
UNICORE_CMS_PYTHON_VENV = '/path/to/bin/python'

REPO_WORKSPACE = '.test_repo_dir'
FRONTEND_REPO_PATH = abspath(REPO_WORKSPACE, 'frontend')
CMS_REPO_PATH = abspath(REPO_WORKSPACE, 'cms')

CONFIG_WORKSPACE = '.test_config_dir'
SUPERVISOR_CONFIGS_PATH = abspath(CONFIG_WORKSPACE, 'supervisor')
NGINX_CONFIGS_PATH = abspath(CONFIG_WORKSPACE, 'nginx')
FRONTEND_SETTINGS_OUTPUT_PATH = abspath(
    CONFIG_WORKSPACE, 'frontend_settings')
CMS_SETTINGS_OUTPUT_PATH = abspath(CONFIG_WORKSPACE, 'cms_settings')
FRONTEND_SOCKETS_PATH = abspath(CONFIG_WORKSPACE, 'frontend_sockets')
CMS_SOCKETS_PATH = abspath(CONFIG_WORKSPACE, 'cms_sockets')

RAVEN_DSN_FRONTEND_QA = 'raven-qa'
RAVEN_DSN_FRONTEND_PROD = 'raven-prod'

RAVEN_DSN_CMS_QA = 'raven-cms-qa'
RAVEN_DSN_CMS_PROD = 'raven-cms-prod'
