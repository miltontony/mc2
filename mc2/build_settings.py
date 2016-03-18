# settings.py for performing collectstatic and other "build-time" operations

from mc2.static_settings import *  # noqa

SECRET_KEY = 'secret'

# For some reason Django wants these
MESOS_DEFAULT_INSTANCES = 1
MESOS_DEFAULT_CPU_SHARE = 0.1
MESOS_DEFAULT_MEMORY_ALLOCATION = 128.0
