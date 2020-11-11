# settings.py for Docker containers running MC2

# Inspired by the settings.py from the official Sentry Docker image:
# https://github.com/getsentry/docker-sentry/blob/445f76edb8edacfa8e0010df7b2881119a29b4a5/8.2/sentry.conf.py

# For Docker, the following environment variables are supported:
#  DEBUG (False)
#  MC2_DB_URL
#  MC2_POSTGRES_HOST* (or MC2_DB_URL)
#  MC2_POSTGRES_PORT ('')
#  MC2_DB_NAME ('postgres')
#  MC2_DB_USER ('postgres')
#  MC2_DB_PASSWORD ('')
#  MC2_REDIS_HOST*
#  MC2_REDIS_PORT ('6379')
#  MC2_REDIS_DB ('0')
#  MC2_MARATHON_HOST*
#  MC2_MARATHON_PORT ('8080')
#  MC2_MESOS_SLAVE_PORT ('5051')
#  MC2_MARATHON_DEFAULT_VOLUME_PATH ('/volume/')
#  MC2_APP_DOMAIN ('127.0.0.1.xip.io')
#  MESOS_DEFAULT_INSTANCES (1)
#  MESOS_DEFAULT_CPU_SHARE (0.1)
#  MESOS_DEFAULT_MEMORY_ALLOCATION (128.0)
#  MC2_LOGDRIVER_PATH ('/logdriver/')
#  MC2_LOGDRIVER_BACKLOG (0)
#  MC2_RAVEN_DSN
#  MC2_SERVER_EMAIL ('root@localhost')
#  MC2_EMAIL_HOST
#  MC2_EMAIL_PORT (25)
#  MC2_EMAIL_USER ('')
#  MC2_EMAIL_PASSWORD ('')
#  MC2_SA_GOOGLE_OAUTH2_KEY ('')
#  MC2_SA_GOOGLE_OAUTH2_SECRET ('')
#  MC2_SA_WHITELISTED_DOMAINS ([])
#  MC2_SECRET_KEY*
import os
import os.path

import dj_database_url

from mc2.static_settings import *  # noqa


def bool_env(var):
    value = os.environ.get(var)
    if not value:
        return False
    value = value.lower()
    if value in ('y', 'yes', 't', 'true', '1'):
        return True
    if value in ('n', 'no', 'f', 'false', '0'):
        return False

CONF_ROOT = os.path.dirname(__file__)
DEBUG = bool_env('DEBUG')
TEMPLATE_DEBUG = DEBUG

############
# Postgres #
############

database_url = os.environ.get('MC2_DB_URL')
if database_url:
    DATABASES = {
        'default': dj_database_url.parse(database_url)
    }
else:
    postgres = (os.environ.get('MC2_POSTGRES_HOST') or
                (os.environ.get('POSTGRES_PORT_5432_TCP_ADDR') and 'postgres'))
    if postgres:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': (
                    os.environ.get('MC2_DB_NAME') or
                    os.environ.get('POSTGRES_ENV_POSTGRES_USER') or
                    'postgres'
                ),
                'USER': (
                    os.environ.get('MC2_DB_USER') or
                    os.environ.get('POSTGRES_ENV_POSTGRES_USER') or
                    'postgres'
                ),
                'PASSWORD': (
                    os.environ.get('MC2_DB_PASSWORD') or
                    os.environ.get('POSTGRES_ENV_POSTGRES_PASSWORD') or
                    ''
                ),
                'HOST': postgres,
                'PORT': os.environ.get('MC2_POSTGRES_PORT') or '',
            },
        }
    else:
        raise Exception(
            'Error: POSTGRES_PORT_5432_TCP_ADDR (or MC2_POSTGRES_HOST) is '
            'undefined, did you forget to `--link` a postgres container?'
        )

#########
# Redis #
#########

# Generic Redis configuration used as defaults for various things.

redis = (os.environ.get('MC2_REDIS_HOST') or
         (os.environ.get('REDIS_PORT_6379_TCP_ADDR') and 'redis'))
if not redis:
    raise Exception('Error: REDIS_PORT_6379_TCP_ADDR (or MC2_REDIS_HOST) is '
                    'undefined, did you forget to `--link` a redis container?')

redis_port = os.environ.get('MC2_REDIS_PORT') or '6379'
redis_db = os.environ.get('MC2_REDIS_DB') or '0'

#########
# Cache #
#########

# A primary cache is required for things such as processing events
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': redis + ':' + redis_port,
        'OPTIONS': {
            'DB': redis_db,
        }
    }
}

#########
# Queue #
#########

CELERY_ALWAYS_EAGER = False
BROKER_URL = 'redis://' + redis + ':' + redis_port + '/' + redis_db
CELERY_RESULT_BACKEND = BROKER_URL

# Uncomment if you're running in DEBUG mode and you want to skip the broker
# and execute tasks immediate instead of deferring them to the queue / workers.
CELERY_ALWAYS_EAGER = DEBUG

# Tell Celery where to find the tasks
CELERY_IMPORTS = ('mc2.tasks', )
CELERY_ACCEPT_CONTENT = ['json']

##################
# Mesos/Marathon #
##################
marathon = (
    os.environ.get('MC2_MARATHON_HOST') or
    (os.environ.get('MARATHON_PORT_8080_TCP_ADDR') and 'marathon')
)
if not marathon:
    raise Exception(
        'Error: MARATHON_PORT_8080_TCP_ADDR (or MC2_MARATHON_HOST) is '
        'undefined, did you forget to `--link` a marathon container?'
    )

marathon_port = os.environ.get('MC2_MARATHON_PORT') or '8080'
MESOS_MARATHON_HOST = marathon + ':' + marathon_port

MESOS_HTTP_PORT = os.environ.get('MC2_MESOS_SLAVE_PORT') or '5051'

MARATHON_DEFAULT_VOLUME_PATH = (
    os.environ.get('MC2_MARATHON_DEFAULT_VOLUME_PATH') or '/volume/'
)

# Domain name for apps launched by MC2
HUB_DOMAIN = os.environ.get('MC2_APP_DOMAIN') or '127.0.0.1.xip.io'

# TODO: Add MC2_ prefix to env vars
MESOS_DEFAULT_INSTANCES = int(os.environ.get('MESOS_DEFAULT_INSTANCES') or 1)
MESOS_DEFAULT_CPU_SHARE = (
    float(os.environ.get('MESOS_DEFAULT_CPU_SHARE') or 0.1)
)
MESOS_DEFAULT_MEMORY_ALLOCATION = (
    float(os.environ.get('MESOS_DEFAULT_MEMORY_ALLOCATION') or 128.0)
)

#############
# Logdriver #
#############
LOGDRIVER_PATH = os.environ.get('MC2_LOGDRIVER_PATH') or '/logdriver/'
LOGDRIVER_BACKLOG = os.environ.get('MC2_LOGDRIVER_BACKLOG') or 0

##################
# Raven (Sentry) #
##################
raven_dsn = os.environ.get('MC2_RAVEN_DSN')
RAVEN_CONFIG = {'dsn': raven_dsn} if raven_dsn else {}

###############
# Mail Server #
###############

# For more information check Django's documentation:
# https://docs.djangoproject.com/en/1.6/topics/email/

email = (os.environ.get('MC2_EMAIL_HOST') or
         (os.environ.get('SMTP_PORT_25_TCP_ADDR') and 'smtp'))
if email:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = email
    EMAIL_PORT = int(os.environ.get('MC2_EMAIL_PORT') or 25)
    EMAIL_HOST_USER = os.environ.get('MC2_EMAIL_USER') or ''
    EMAIL_HOST_PASSWORD = os.environ.get('MC2_EMAIL_PASSWORD') or ''
else:
    EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# The email address to send on behalf of
SERVER_EMAIL = os.environ.get('MC2_SERVER_EMAIL') or 'root@localhost'

###############
# Social auth #
###############
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('MC2_SA_GOOGLE_OAUTH2_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get(
    'MC2_SA_GOOGLE_OAUTH2_SECRET', '')

social_auth_whitelisted_domains = os.environ.get('MC2_SA_WHITELISTED_DOMAINS')
if social_auth_whitelisted_domains:
    SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = \
        [d.strip() for d in social_auth_whitelisted_domains.split(',')]

# If this value ever becomes compromised, it's important to regenerate your
# MC2_SECRET_KEY. Changing this value will result in all current sessions
# being invalidated.
SECRET_KEY = os.environ.get('MC2_SECRET_KEY')
if not SECRET_KEY:
    raise Exception('Error: MC2_SECRET_KEY is undefined')

if len(SECRET_KEY) < 32:
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print('!!                CAUTION                    !!')
    print('!! Your SECRET_KEY is potentially insecure.  !!')
    print('!! We recommend at least 32 characters long. !!')
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
