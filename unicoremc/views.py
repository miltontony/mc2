import json
import os.path

from apiclient import errors
from oauth2client.client import AccessTokenCredentialsError

from django.conf import settings
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.http import (
    HttpResponse, HttpResponseBadRequest, HttpResponseServerError,
    HttpResponseForbidden, HttpResponseNotFound)
from django.contrib.auth.decorators import (
    login_required, user_passes_test)
from django.contrib.auth.models import User
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import ListView, TemplateView, RedirectView
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages

from organizations.utils import org_permission_required, active_organization

from unicoremc.models import Project, Localisation, AppType, ProjectRepo
from unicoremc.forms import ProjectForm
from unicoremc import constants, exceptions
from unicoremc import tasks, utils


def repos_json(request):
    # no login_required because repos are public
    refresh = request.GET.get('refresh', 'false') == 'true'
    repos = utils.get_repos(refresh)
    return HttpResponse(json.dumps(repos), content_type='application/json')


@login_required
def teams_json(request):
    # login_required because teams aren't public
    teams = utils.get_teams()
    return HttpResponse(json.dumps(teams), content_type='application/json')


class ProjectViewMixin(View):
    pk_url_kwarg = 'project_id'
    permissions = []
    social_auth = None

    @classmethod
    def as_view(cls):
        view = super(ProjectViewMixin, cls).as_view()

        if cls.social_auth:
            view = user_passes_test(
                lambda u: u.social_auth.filter(
                    provider=cls.social_auth).exists(),
                login_url=reverse_lazy(
                    'social:begin', args=(cls.social_auth,)))(view)

        if cls.permissions:
            view = org_permission_required(cls.permissions)(view)

        return login_required(view)

    def dispatch(self, request, *args, **kwargs):
        self.organization = active_organization(request)
        return super(ProjectViewMixin, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.organization is None:
            if self.request.user.is_superuser:
                return Project.objects.all()
            return Project.objects.none()
        return Project.objects.filter(organization=self.organization)


class NewProjectView(ProjectViewMixin, TemplateView):
    # TODO: base this on CreateView instead of TemplateView
    template_name = 'unicoremc/new_project.html'
    permissions = ['unicoremc.add_project']

    def get_context_data(self):
        project_pks = self.get_queryset().values_list('pk', flat=True)

        context = super(NewProjectView, self).get_context_data()
        context.update({
            'countries': constants.COUNTRY_CHOICES,
            'languages': Localisation.objects.all(),
            'app_types': AppType.objects.all(),
            'project_repos': ProjectRepo.objects.filter(
                project__in=project_pks,
                project__state='done'),
        })
        return context

    def post(self, request, *args, **kwargs):
        app_type = request.POST.get('app_type')
        app_type = AppType.objects.get(pk=int(app_type))
        base_repo = request.POST.get('base_repo')
        project_repos = request.POST.getlist('project_repos[]')
        repo_count = len(project_repos) + (1 if base_repo else 0)

        # validate base repos and app type
        if not repo_count:
            return HttpResponseBadRequest('No repo selected')
        if (repo_count > 1 and app_type.project_type == AppType.UNICORE_CMS):
            return HttpResponseBadRequest(
                '%s does not support multiple repos' % (AppType.UNICORE_CMS,))

        country = request.POST.get('country')
        user_id = request.POST.get('user_id')
        team_id = request.POST.get('team_id')
        docker_cmd = request.POST.get('docker_cmd')

        user = User.objects.get(pk=user_id)

        project, created = Project.objects.get_or_create(
            application_type=app_type,
            country=country,
            defaults={
                'team_id': int(team_id),
                'owner': user,
                'organization': self.organization,
                'docker_cmd':
                    docker_cmd or
                    utils.get_default_docker_cmd(app_type, country)
            })
        project.external_repos.add(*project_repos)
        if base_repo:
            ProjectRepo.objects.get_or_create(
                project=project,
                defaults={'base_url': base_repo})

        # For consistency with existing apps, all new apps will also have
        # country domain urls in addition to the generic urls
        project.frontend_custom_domain = project.get_country_domain()
        project.cms_custom_domain = 'cms.%s' % project.get_country_domain()
        project.save()

        if created:
            tasks.start_new_project.delay(project.id)

        return HttpResponse(json.dumps({'success': True}),
                            content_type='application/json')


class HomepageView(ProjectViewMixin, ListView):
    template_name = 'unicoremc/home.html'


class ProjectEditView(ProjectViewMixin, UpdateView):
    form_class = ProjectForm
    template_name = 'unicoremc/advanced.html'
    permissions = ['unicoremc.change_project']

    def get_success_url(self):
        return reverse("home")

    def form_valid(self, form):
        response = super(ProjectEditView, self).form_valid(form)
        project = self.get_object()
        Project.objects.filter(
            pk=project.pk).update(project_version=F('project_version') + 1)

        project = self.get_object()
        project.create_or_update_hub_app()
        project.create_pyramid_settings()
        project.create_nginx()

        try:
            project.update_marathon_app()
        except exceptions.MarathonApiException:
            messages.info(self.request, 'Unable to update project in marathon')
        return response


class ManageGAView(ProjectViewMixin, TemplateView):
    # TODO: base this on UpdateView instead of TemplateView
    template_name = 'unicoremc/manage_ga.html'
    permissions = ['unicoremc.change_project']
    social_auth = 'google-oauth2'

    def get_context_data(self):
        social = self.request.user.social_auth.get(provider='google-oauth2')
        accounts = utils.get_ga_accounts(social.extra_data['access_token'])

        context = super(ManageGAView, self).get_context_data()
        context.update({
            'projects': self.get_queryset().filter(state='done'),
            'accounts': [
                {'id': a.get('id'), 'name': a.get('name')} for a in accounts],
        })
        return context

    def get(self, request, *args, **kwargs):
        try:
            return super(ManageGAView, self).get(request, *args, **kwargs)
        except AccessTokenCredentialsError:
            return redirect('social:begin', 'google-oauth2')

    def post(self, request, *args, **kwargs):
        project_id = request.POST.get('project_id')
        account_id = request.POST.get('account_id')
        social = request.user.social_auth.get(provider='google-oauth2')
        access_token = social.extra_data['access_token']
        project = get_object_or_404(self.get_queryset(), pk=project_id)

        if not project.ga_profile_id:
            try:
                name = u'%s %s' % (
                    project.app_type.upper(), project.get_country_display())
                new_profile_id = utils.create_ga_profile(
                    access_token, account_id, project.frontend_url(), name)

                project.ga_profile_id = new_profile_id
                project.ga_account_id = account_id
                project.save()
                project.create_pyramid_settings()

                return HttpResponse(
                    json.dumps({'ga_profile_id': new_profile_id}),
                    content_type='application/json')
            except errors.HttpError:
                return HttpResponseServerError("Unable to create new profile")

        return HttpResponseForbidden("Project already has a profile")


class ResetHubAppKeyView(ProjectViewMixin, SingleObjectMixin, RedirectView):
    permissions = ['unicoremc.change_project']
    permanent = False
    pattern_name = 'advanced'

    def get(self, request, *args, **kwargs):
        project = self.get_object()
        app = project.hub_app()
        if app is not None:
            app.reset_key()
            project.create_pyramid_settings()
        return super(ResetHubAppKeyView, self).get(request, *args, **kwargs)


class AppLogView(ProjectViewMixin, TemplateView):
    template_name = 'unicoremc/app_logs.html'

    def get_context_data(self, *args, **kwargs):
        context = super(AppLogView, self).get_context_data(*args, **kwargs)
        project = get_object_or_404(self.get_queryset(),
                                    pk=kwargs['project_id'])
        tasks = project.infra_manager.get_project_marathon_tasks()
        context.update({
            'project': project,
            'tasks': tasks,
            'task_ids': [t['id'].split('.', 1)[1] for t in tasks],
        })
        return context


class AppEventSourceView(ProjectViewMixin, View):

    def get(self, request, project_id, task_id, path):
        project = get_object_or_404(Project, pk=project_id)
        if path not in ['stdout', 'stderr']:
            return HttpResponseNotFound('File not found.')

        # NOTE: I'm piecing together the app_id and task_id here
        #       so as to not need to expose both in the templates.
        task = project.infra_manager.get_project_task_log_info(
            '%s.%s' % (project.app_id, task_id))

        response = HttpResponse()
        response['X-Accel-Redirect'] = os.path.join(
            settings.LOGDRIVER_PATH, task['task_host'],
            task['task_dir'], path)
        response['X-Accel-Buffering'] = 'no'
        return response
