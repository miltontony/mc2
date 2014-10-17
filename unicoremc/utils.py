import ConfigParser
import os

from django.conf import settings


class Supervisor(object):
    def __init__(self, filename, fullpath):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(fullpath)
        self.filename = filename
        self.all = [
            {
                'section': section,
                'items': self.config.items(section)
            }
            for section in self.config.sections()
        ]


class NodeManager(object):
    def __init__(self):
        self.supervisor_path = settings.SUPERVISOR_CONFIGS_PATH
        self.nginx_path = settings.NGINX_CONFIGS_PATH
        self.supervisor_configs = []
        self.load_supervisor_configs()

    def load_supervisor_configs(self):
        if os.path.exists(self.supervisor_path):
            self.supervisor_configs = [
                Supervisor(f, os.path.join(self.supervisor_path, f))
                for f in os.listdir(self.supervisor_path)
                if os.path.isfile(os.path.join(self.supervisor_path, f)) and
                f.startswith('unicore_cms')
            ]

    def find_supervisor(self, filename):
        if os.path.exists(os.path.join(self.supervisor_path, filename)):
            for supervisor in self.supervisor_configs:
                if supervisor.filename == filename:
                    return supervisor
        return None
