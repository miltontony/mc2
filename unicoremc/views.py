from django.shortcuts import render
from django.http import Http404
from django.contrib.auth.decorators import login_required

from unicoremc.utils import NodeManager
from unicoremc import constants


def home(request):
    return render(request, 'unicoremc/home.html', {})


@login_required(login_url='/')
def list_supervisor_configs_view(request, *args, **kwargs):
    context = {
        'supervisor_configs': NodeManager().supervisor_configs,
    }
    return render(request, 'unicoremc/supervisor.html', context)


@login_required(login_url='/')
def list_nginx_configs_view(request, *args, **kwargs):
    context = {
        'nginx_configs': NodeManager().nginx_configs,
    }
    return render(request, 'unicoremc/nginx.html', context)


@login_required(login_url='/')
def supervisor_config_view(request, *args, **kwargs):
    filename = request.GET.get('filename')
    if filename:
        context = {
            'config': NodeManager().find_supervisor(filename),
        }
    else:
        raise Http404

    return render(request, 'unicoremc/supervisor_detail.html', context)


@login_required(login_url='/')
def nginx_config_view(request, *args, **kwargs):
    filename = request.GET.get('filename')
    if filename:
        context = {
            'config': NodeManager().find_nginx(filename),
        }
    else:
        raise Http404

    return render(request, 'unicoremc/nginx_detail.html', context)


@login_required(login_url='/')
def new_project_view(request, *args, **kwargs):
    context = {
        'countries': constants.COUNTRIES
    }
    return render(request, 'unicoremc/new_project.html', context)


@login_required(login_url='/')
def test_ajax_function(request, *args, **kwargs):
    from time import sleep
    sleep(2)
    context = {
    }
    return render(request, 'unicoremc/new_project.html', context)
