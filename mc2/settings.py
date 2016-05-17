# Django settings for skeleton project.

from os.path import abspath, dirname, join
from os import environ
import dj_database_url

# Tell psycopg2cffi to impersonate psycopg2
from psycopg2cffi import compat
compat.register()


def bool_env(val):
    """Replaces string based environment values with Python booleans"""
    return True if environ.get(val, False) == 'True' else False

# Environment Variables
SECRET_KEY = environ.get('SECRET_KEY', 'please-change-me')
PROJECT_ROOT = environ.get(
    'PROJECT_ROOT', dirname(dirname(abspath(__file__))))
MESOS_DEFAULT_MEMORY_ALLOCATION = environ.get(
    'MESOS_DEFAULT_MEMORY_ALLOCATION', 128.0)
MESOS_MARATHON_HOST = environ.get(
    'MESOS_MARATHON_HOST', 'http://localhost:8080')
MESOS_HTTP_PORT = environ.get('MESOS_HTTP_PORT', 5051)
MESOS_DEFAULT_CPU_SHARE = environ.get('MESOS_DEFAULT_CPU_SHARE', 0.1)
MESOS_DEFAULT_INSTANCES = environ.get('MESOS_DEFAULT_INSTANCES', 1)
MESOS_DEFAULT_GRACE_PERIOD_SECONDS = environ.get(
    'MESOS_DEFAULT_GRACE_PERIOD_SECONDS', 60)
MESOS_DEFAULT_INTERVAL_SECONDS = environ.get(
    'MESOS_DEFAULT_INTERVAL_SECONDS', 10)
MESOS_DEFAULT_TIMEOUT_SECONDS = environ.get(
    'MESOS_DEFAULT_TIMEOUT_SECONDS', 20)
MARATHON_DEFAULT_VOLUME_PATH = environ.get(
    'MARATHON_DEFAULT_VOLUME_PATH', '/volume/')

HUB_DOMAIN = environ.get('HUB_DOMAIN', 'seed.p16n.org')

# Configured at Nginx for internal redirect
LOGDRIVER_PATH = environ.get('LOGDRIVER_PATH', '/logdriver/')
LOGDRIVER_BACKLOG = environ.get('LOGDRIVER_BACKLOG', 1)

# Sentry configuration
RAVEN_DSN = environ.get('RAVEN_DSN')
RAVEN_CONFIG = {'dsn': RAVEN_DSN} if RAVEN_DSN else {}

# Social Auth
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = environ.get(
    'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = environ.get(
    'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', '')

SOCIAL_AUTH_WHITELISTED_DOMAINS = environ.get(
    'SOCIAL_AUTH_WHITELISTED_DOMAINS')
if SOCIAL_AUTH_WHITELISTED_DOMAINS:
    SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = \
        [d.strip() for d in SOCIAL_AUTH_WHITELISTED_DOMAINS.split(',')]

# SMTP Settings
EMAIL_HOST = environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = environ.get('EMAIL_PORT', 25)
EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD', '')

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
    'mc2.organizations.context_processors.org',
    'mc2.context_processors.default_forms',
    'mc2.context_processors.app_version',
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
    'raven.contrib.django.raven_compat',
    'debug_toolbar',

    'social.apps.django_app.default',
    'mc2',
    'mc2.controllers.docker',
    'mc2.controllers.base',
    'mc2.controllers',
    'mc2.organizations',

    'grappelli',
    'django.contrib.admin',

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

# Celery configuration options
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Uncomment if you're running in DEBUG mode and you want to skip the broker
# and execute tasks immediate instead of deferring them to the queue / workers.
CELERY_ALWAYS_EAGER = DEBUG

# Tell Celery where to find the tasks
CELERY_IMPORTS = ('mc2.controllers.base.tasks', )
CELERY_ACCEPT_CONTENT = ['json']

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

HUBCLIENT_SETTINGS = None

MAMA_CAS_ATTRIBUTE_CALLBACKS = ('mc2.permissions.custom_attributes',)
