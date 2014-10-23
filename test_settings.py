from project.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'cms_django.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

DEBUG = True
CELERY_ALWAYS_EAGER = DEBUG

CMS_REPO_PATH = abspath('.test_repo_dir')
SUPERVISOR_CONFIGS_PATH = abspath('.test_config_dir')
