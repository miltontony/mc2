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

FRONTEND_REPO_PATH = abspath('.test_repo_dir', 'frontend')
CMS_REPO_PATH = abspath('.test_repo_dir', 'cms')

SUPERVISOR_CONFIGS_PATH = abspath('.test_config_dir', 'supervisor')
NGINX_CONFIGS_PATH = abspath('.test_config_dir', 'nginx')
FRONTEND_SETTINGS_OUTPUT_PATH = abspath('.test_config_dir', 'frontend_settings')
CMS_SETTINGS_OUTPUT_PATH = abspath('.test_config_dir', 'cms_settings')
SOCKETS_PATH = abspath('.test_config_dir', 'sockets')
