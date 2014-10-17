from django.contrib import admin
from django.shortcuts import render
from django.http import Http404

from unicoremc.utils import NodeManager


@admin.site.register_view('supervisor/', 'Supervisor Configs')
def list_supervisor_configs_view(request, *args, **kwargs):
    context = {
        'supervisor_configs': NodeManager().supervisor_configs,
    }
    return render(request, 'admin/unicoremc/supervisor.html', context)


@admin.site.register_view('supervisor/config/', 'Supervisor Configs Detail')
def supervisor_config_view(request, *args, **kwargs):
    filename = request.GET.get('filename')
    if filename:
        context = {
            'config': NodeManager().find_supervisor(filename),
        }
    else:
        raise Http404

    return render(request, 'admin/unicoremc/supervisor_detail.html', context)
