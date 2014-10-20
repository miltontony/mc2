import json

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from unicoremc import constants


def home(request):
    return render(request, 'unicoremc/home.html', {})


@login_required
def new_project_view(request, *args, **kwargs):
    context = {
        'countries': constants.COUNTRIES
    }
    return render(request, 'unicoremc/new_project.html', context)


@login_required
def test_ajax_function(request, *args, **kwargs):
    from time import sleep
    sleep(2)
    return HttpResponse(json.dumps({'some': 'json'}),
                        mimetype='application/json')
