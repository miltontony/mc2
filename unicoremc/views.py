import json

from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse

from unicoremc.models import Project, Localisation
from unicoremc.forms import ProjectForm
from unicoremc.states import ProjectWorkflow
from unicoremc import constants
from unicoremc import tasks


@login_required
@permission_required('project.can_change')
def new_project_view(request, *args, **kwargs):
    social = request.user.social_auth.get(provider='github')
    access_token = social.extra_data['access_token']
    context = {
        'countries': constants.COUNTRY_CHOICES,
        'languages': Localisation.objects.all(),
        'access_token': access_token,
    }
    return render(request, 'unicoremc/new_project.html', context)


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


@login_required
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
            'id': p.pk
        } for p in projects]
    ))
