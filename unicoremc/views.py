import json

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from unicoremc.models import Project, Localisation
from unicoremc.states import ProjectWorkflow
from unicoremc import constants
from unicoremc import tasks


@login_required
def new_project_view(request, *args, **kwargs):
    social = request.user.social_auth.get(provider='github')
    access_token = social.extra_data['access_token']
    context = {
        'countries': constants.COUNTRIES,
        'languages': Localisation.objects.all(),
        'access_token': access_token,
    }
    return render(request, 'unicoremc/new_project.html', context)


@csrf_exempt
def start_new_project(request, *args, **kwargs):
    if request.method == 'POST':

        app_type = request.POST.get('app_type')
        base_repo = request.POST.get('base_repo')
        country = request.POST.get('country')
        access_token = request.POST.get('access_token')
        user_id = request.POST.get('user_id')
        team_id = request.POST.get('team_id')

        user = User.objects.get(pk=user_id)
        project, created = Project.objects.get_or_create(
            app_type=app_type,
            base_repo_url=base_repo,
            country=country,
            team_id=int(team_id),
            owner=user)

        if created:
            tasks.start_new_project.delay(project.id, access_token)

    return HttpResponse(json.dumps({'success': True}),
                        mimetype='application/json')


def projects_progress(request, *args, **kwargs):
    projects = Project.objects.all()
    return HttpResponse(json.dumps(
        [{
            'app_type': p.get_app_type_display(),
            'base_repo': p.base_repo_url,
            'state': ProjectWorkflow(instance=p).get_state(),
            'country': p.get_country_display(),
            'repo_url': p.repo_url,
            'frontend_url': p.frontend_url(),
            'cms_url': p.cms_url(),
        } for p in projects]
    ))
