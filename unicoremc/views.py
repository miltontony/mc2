import ConfigParser
import os

from django.contrib import admin
from django.conf import settings
from django.shortcuts import render


def read_config(f):
    config = ConfigParser.RawConfigParser()
    config.read(f)

    return [
        {
            'name': section,
            'items': config.items(section)
        }
        for section in config.sections()
    ]


@admin.site.register_view('apps/', 'Apps')
def apps_view(request, *args, **kwargs):
    supervisor_path = settings.SUPERVISOR_CONFIGS_PATH
    supervisor_configs = []
    if os.path.exists(supervisor_path):
        supervisor_configs = [
            {
                'name': f,
                'sections': read_config(os.path.join(supervisor_path, f))
            }
            for f in os.listdir(supervisor_path)
            if os.path.isfile(os.path.join(supervisor_path, f)) and
            f.startswith('unicore_cms')
        ]
    context = {
        'supervisor_configs': supervisor_configs,
    }
    return render(request, 'admin/unicoremc/apps.html', context)
