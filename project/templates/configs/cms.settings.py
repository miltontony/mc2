from project.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django_cms_{{app_type}}_{{country}}',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

GIT_REPO_PATH = '{{repo_path}}'
GIT_REPO_URL = '{{ git_repo_uri }}'

ELASTIC_GIT_INDEX_PREFIX = 'unicore_cms_{{app_type}}_{{country}}'

CELERY_ALWAYS_EAGER = False
BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

RAVEN_CONFIG = {'dsn': '{{raven_dsn_uri}}'}
SSH_PRIVKEY_PATH = "/home/ubuntu/.ssh/django_cms"
SSH_PUBKEY_PATH = "/home/ubuntu/.ssh/django_cms.pub"

DEBUG = False
TEMPLATE_DEBUG = False
