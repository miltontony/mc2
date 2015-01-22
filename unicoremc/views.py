import json

import httplib2

from apiclient import discovery, errors
from oauth2client import client

from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.http import (
    HttpResponse, HttpResponseBadRequest, HttpResponseServerError)
from django.contrib.auth.decorators import (
    login_required, permission_required, user_passes_test)
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse

from unicoremc.models import Project, Localisation
from unicoremc.forms import ProjectForm
from unicoremc.states import ProjectWorkflow
from unicoremc import constants
from unicoremc import tasks


import requests


def get_all_repos(request):
    url = ('https://api.github.com/orgs/universalcore/'
           'repos?type=public&per_page=100&page=%s')
    pageNum = 1
    repos = []
    while True:
        response = requests.get(url % pageNum)
        data = response.json()
        if not data:
            break
        repos.extend(data)
        pageNum += 1

    return HttpResponse(json.dumps(repos), content_type='application/json')


def get_ga_accounts(access_token):
    credentials = client.AccessTokenCredentials(
        access_token,
        'unicore-hub/1.0')
    http = credentials.authorize(http=httplib2.Http())
    service = discovery.build('analytics', 'v3', http=http)
    resp = service.management().accounts().list().execute()
    return resp.get('items', [])


def create_ga_profile(access_token, account_id):
    credentials = client.AccessTokenCredentials(
        access_token,
        'unicore-hub/1.0')
    http = credentials.authorize(http=httplib2.Http())
    service = discovery.build('analytics', 'v3', http=http)

    resp = service.management().webproperties().insert(
        accountId='123456',
        body={
            'websiteUrl': 'http://www.examplepetstore.com',
            'name': 'Example Store'
        }
    ).execute()
    return resp.get("id")


@login_required
@permission_required('project.can_change')
@user_passes_test(
    lambda u: u.social_auth.filter(provider='github').exists(),
    login_url='/social/login/github/')
def new_project_view(request, *args, **kwargs):
    social = request.user.social_auth.get(provider='github')
    access_token = social.extra_data['access_token']
    context = {
        'countries': constants.COUNTRY_CHOICES,
        'languages': Localisation.objects.all(),
        'app_types': Project.APP_TYPES,
        'access_token': access_token,
    }
    return render(request, 'unicoremc/new_project.html', context)


@login_required
@permission_required('project.can_change')
@user_passes_test(
    lambda u: u.social_auth.filter(provider='google-oauth2').exists(),
    login_url='/social/login/google-oauth2/')
def manage_ga_view(request, *args, **kwargs):
    social = request.user.social_auth.get(provider='google-oauth2')
    access_token = social.extra_data['access_token']

    context = {
        'projects': Project.objects.filter(state='done'),
        'access_token': access_token,
        'accounts': [
            {'id': a.get('id'), 'name': a.get('name')}
            for a in get_ga_accounts(access_token)],
    }
    return render(request, 'unicoremc/manage_ga.html', context)


class ProjectEditView(UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'unicoremc/advanced.html'

    def get_success_url(self):
        return reverse("home")

    def get_object(self, queryset=None):
        return get_object_or_404(Project, pk=self.kwargs['project_id'])

    def form_valid(self, form):
        response = super(ProjectEditView, self).form_valid(form)
        project = self.get_object()
        Project.objects.filter(
            pk=project.pk).update(project_version=F('project_version') + 1)

        project = self.get_object()
        project.create_pyramid_settings()
        return response


@csrf_exempt
@login_required
@permission_required('project.can_change')
@user_passes_test(
    lambda u: u.social_auth.filter(provider='github').exists(),
    login_url='/social/login/github/')
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
                        content_type='application/json')


@csrf_exempt
@login_required
@permission_required('project.can_change')
def manage_ga_new(request, *args, **kwargs):
    if request.method == 'POST':

        project_id = request.POST.get('project_id')
        account_id = request.POST.get('account_id')
        access_token = request.POST.get('access_token')
        project = get_object_or_404(Project, pk=project_id)

        if not project.ga_profile_id:
            try:
                new_profile_id = create_ga_profile(access_token, account_id)
                new_profile_id = 'new id'
                project.ga_profile_id = new_profile_id
                project.ga_account_id = account_id
                project.save()

                return HttpResponse(
                    json.dumps({'ga_profile_id': new_profile_id}),
                    content_type='application/json')
            except errors.HttpError:
                return HttpResponseServerError("Unable to create new profile")

    return HttpResponseBadRequest("You can only call this using a POST")


@login_required
def projects_progress(request, *args, **kwargs):
    projects = Project.objects.all()
    return HttpResponse(json.dumps(
        [{
            'app_type': p.get_app_type_display(),
            'base_repo': p.base_repo_url,
            'state': ProjectWorkflow(instance=p).get_state(),
            'country': p.get_country_display(),
            'repo_url': p.repo_url or '',
            'frontend_url': p.frontend_url(),
            'cms_url': p.cms_url(),
            'ga_profile_id': p.ga_profile_id,
            'available_languages': [
                l.get_code() for l in p.available_languages.all()],
            'id': p.pk
        } for p in projects]
    ))
