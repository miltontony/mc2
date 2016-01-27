# Django settings for skeleton project.

from os.path import abspath, dirname, join
from os import environ
import dj_database_url


def bool_env(val):
    """Replaces string based environment values with Python booleans"""
    return True if environ.get(val, False) == 'True' else False

# Environment Variables
SECRET_KEY = environ.get('SECRET_KEY') or 'please-change-me'
PROJECT_ROOT = (
    environ.get('PROJECT_ROOT') or dirname(dirname(abspath(__file__))))
MESOS_DEFAULT_MEMORY_ALLOCATION = (
    environ.get('MESOS_DEFAULT_MEMORY_ALLOCATION') or 128.0)
MESOS_MARATHON_HOST = (
    environ.get('MESOS_MARATHON_HOST') or 'http://localhost:8080')
MESOS_HTTP_PORT = environ.get('MESOS_HTTP_PORT') or 5051
MESOS_DEFAULT_CPU_SHARE = environ.get('MESOS_DEFAULT_CPU_SHARE') or 0.1
MESOS_DEFAULT_INSTANCES = environ.get('MESOS_DEFAULT_INSTANCES') or 1
MARATHON_DEFAULT_VOLUME_PATH = (
    environ.get('MARATHON_DEFAULT_VOLUME_PATH') or '/volume/')

# Configured at Nginx for internal redirect
LOGDRIVER_PATH = (
    environ.get('LOGDRIVER_PATH') or '/logdriver/')
LOGDRIVER_BACKLOG = (
    environ.get('LOGDRIVER_BACKLOG') or 0)

# Sentry configuration
RAVEN_DSN = environ.get('RAVEN_DSN')
RAVEN_CONFIG = {'dsn': RAVEN_DSN} if RAVEN_DSN else {}

# Social Auth
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = (
    environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY') or '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = (
    environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET') or '')

SOCIAL_AUTH_WHITELISTED_DOMAINS = environ.get(
    'SOCIAL_AUTH_WHITELISTED_DOMAINS')
if SOCIAL_AUTH_WHITELISTED_DOMAINS:
    SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = \
        [d.strip() for d in SOCIAL_AUTH_WHITELISTED_DOMAINS.split(',')]

DEBUG = bool_env('DEBUG')
TEMPLATE_DEBUG = DEBUG


def abspath(*args):
    """convert relative paths to absolute paths relative to PROJECT_ROOT"""
    return join(PROJECT_ROOT, *args)


ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Use `DATABASE_URL` environment variable to specify the database
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///%s' % (join(PROJECT_ROOT, 'mc2.db'),))}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = abspath('media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = abspath('static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'compressor.finders.CompressorFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.filesystem.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
    'ws4redis.context_processors.default',
    'mc2.organizations.context_processors.org',
    'mc2.context_processors.default_forms'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'social.backends.google.GoogleOAuth2',
)

SOCIAL_AUTH_USER_MODEL = 'auth.User'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
FIELDS_STORED_IN_SESSION = ['access_token', ]


ROOT_URLCONF = 'mc2.urls'

# Python dotted path to the WSGI application used by Django's server.
# WSGI_APPLICATION = 'ws4redis.django_runserver.application'

TEMPLATE_DIRS = (
    abspath('puppet_templates'),
    abspath('templates'),
)

INSTALLED_APPS = (
    'polymorphic',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'redis_cache',
    'django_nose',
    'raven.contrib.django.raven_compat',
    'debug_toolbar',

    'social.apps.django_app.default',
    'mc2',
    'mc2.controllers.freebasics',
    'mc2.controllers.docker',
    'mc2.controllers.base',
    'mc2.controllers',
    'mc2.organizations',

    'grappelli',
    'django.contrib.admin',

    'ws4redis',
    'compressor',
    'django_gravatar',
    'mama_cas',
    'djcelery_email',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
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

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 2,
        }
    }
}

GRAPPELLI_ADMIN_TITLE = 'Mission Control'

WS4REDIS_EXPIRE = 1
WEBSOCKET_URL = '/ws/'
WS4REDIS_CONNECTION = {
    'db': 4
}

# Celery configuration options
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Uncomment if you're running in DEBUG mode and you want to skip the broker
# and execute tasks immediate instead of deferring them to the queue / workers.
CELERY_ALWAYS_EAGER = DEBUG

# Tell Celery where to find the tasks
CELERY_IMPORTS = ('mc2.tasks', )

# Defer email sending to Celery, except if we're in debug mode,
# then just print the emails to stdout for debugging.
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CELERY_EMAIL_TASK_CONFIG = {
    'serializer': 'json'
}

# Django debug toolbar
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'ENABLE_STACKTRACES': True,
}
DEBUG_TOOLBAR_PATCH_SETTINGS = False

SOCIAL_AUTH_SESSION_EXPIRATION = True
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/analytics.edit',
    'https://www.googleapis.com/auth/analytics.provision']
SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    'access_type': 'offline',
    'approval_prompt': 'auto'
}

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'mc2.socialauth_pipelines.redirect_if_no_refresh_token',
    'social.pipeline.user.get_username',
    'social.pipeline.social_auth.associate_by_email',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details'
)

# Unicore Settings (not currently in use)
# ---------------------------------------

# Used to distinguish between QA and PROD in naming
DEPLOY_ENVIRONMENT = 'qa'

CMS_SUBDOMAIN = 'qa-content'
HUB_DOMAIN = 'qa-hub.unicore.io'

# path to where repos will be located
FRONTEND_REPO_PATH = abspath('repos', 'frontend')
CMS_REPO_PATH = abspath('repos', 'cms')

CONFIGS_REPO_PATH = abspath('configs')

# path to settings files
SPRINGBOARD_SETTINGS_OUTPUT_PATH = abspath('configs', 'springboard_settings')
FRONTEND_SETTINGS_OUTPUT_PATH = abspath('configs', 'frontend_settings')
CMS_SETTINGS_OUTPUT_PATH = abspath('configs', 'cms_settings')

FRONTEND_SOCKETS_PATH = abspath('configs', 'frontend_sockets')
CMS_SOCKETS_PATH = abspath('configs', 'cms_sockets')

UNICORE_CMS_INSTALL_DIR = '/path/to/unicore-cms-django'
UNICORE_CMS_PYTHON_VENV = '/path/to/bin/python'
UNICORE_CONFIGS_INSTALL_DIR = '/path/to/unicore-configs'

GITHUB_API = 'https://api.github.com/orgs/universalcore/'
GITHUB_HOOKS_API = 'https://api.github.com/repos/universalcore/%(repo)s/hooks'
GITHUB_REPO_NAME_SUFFIX = ''  # used to denote PROD vs QA
GITHUB_USERNAME = ''
GITHUB_TOKEN = ''

RAVEN_DSN_FRONTEND_QA = ''
RAVEN_DSN_FRONTEND_PROD = ''

RAVEN_DSN_CMS_QA = ''
RAVEN_DSN_CMS_PROD = ''

THUMBOR_SECURITY_KEY = ''

ELASTICSEARCH_HOST = 'http://localhost:9200'
UNICORE_DISTRIBUTE_HOST = 'http://localhost:6543'
SERVICE_HOST_IP = '127.0.0.1'

HUBCLIENT_SETTINGS = None

CELERY_ACCEPT_CONTENT = ['json']

MAMA_CAS_ATTRIBUTE_CALLBACKS = (
    'mc2.permissions.custom_attributes',)
