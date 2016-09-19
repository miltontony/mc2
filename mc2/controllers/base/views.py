import json
import os.path
import urllib
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.http import (
    HttpResponse, HttpResponseNotFound,
    HttpResponseNotAllowed, HttpResponseServerError)
from django.contrib.auth.decorators import (
    login_required, user_passes_test)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView, CreateView, FormMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from mc2.organizations.utils import org_permission_required
from mc2.organizations.utils import active_organization
from mc2.organizations.models import Organization
from mc2.controllers.base.models import Controller
from mc2.controllers.base.forms import (
    ControllerFormHelper)
from mc2.controllers.base import exceptions, tasks


@login_required
def update_marathon_exists_json(request, controller_pk):
    controller = get_object_or_404(Controller, pk=controller_pk)

    workflow = controller.get_builder().workflow
    if controller.state == 'done' and not controller.exists_on_marathon():
        workflow.take_action('missing')
        controller.save()
    elif controller.state == 'missing' and controller.exists_on_marathon():
        workflow.take_action('activate')
        controller.save()

    return HttpResponse(
        json.dumps({'state': controller.state}),
        content_type='application/json')


class ControllerViewMixin(FormMixin, View):
    pk_url_kwarg = 'controller_pk'
    permissions = []
    social_auth = None

    @classmethod
    def as_view(cls):
        view = super(ControllerViewMixin, cls).as_view()

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
        return super(
            ControllerViewMixin, self).dispatch(request, *args, **kwargs)

    def get_controllers_queryset(self, request):
        organization = active_organization(request)
        if organization is None:
            if request.user.is_superuser:
                return Controller.objects.all()
            return Controller.objects.none()
        return Controller.objects.filter(organization=organization)

    def get_form(self, *args, **kwargs):
        """
        Return a form with the organizations limited to the organizations
        this user has access to. Returns a form with all availble
        organizations for super users.

        Since mixin is used in views that subclass CreateView or UpdateView
        I am relying on those to provide the `get_form` as implemented
        in the `FormMixin` both of those inherit
        """
        form = FormMixin.get_form(self, *args, **kwargs)
        if self.request.user.is_superuser:
            return form

        form.controller_form.fields['organization'].queryset = (
            self.request.user.organization_set.all())
        return form


class ControllerCreateView(ControllerViewMixin, CreateView):
    form_class = ControllerFormHelper
    template_name = 'controller_edit.html'
    permissions = ['controllers.base.add_controller']

    def get_success_url(self):
        return reverse("home")

    def form_valid(self, form):
        form.controller_form.instance.organization = active_organization(
            self.request)
        form.controller_form.instance.owner = self.request.user
        form.controller_form.instance.save()

        form.env_formset.instance = form.controller_form.instance
        form.link_formset.instance = form.controller_form.instance
        form.label_formset.instance = form.controller_form.instance

        response = super(ControllerCreateView, self).form_valid(form)
        tasks.start_new_controller.delay(form.controller_form.instance.id)
        return response


class ControllerCloneView(ControllerViewMixin, CreateView):
    form_class = ControllerFormHelper
    template_name = 'controller_edit.html'
    permissions = ['controllers.base.add_controller']

    def get_initial(self):
        initial = super(ControllerCloneView, self).get_initial()

        controller = get_object_or_404(
            Controller, pk=self.kwargs.get('controller_pk'))

        initial.update({
            'marathon_cpus': controller.marathon_cpus,
            'marathon_mem': controller.marathon_mem,
            'marathon_instances': controller.marathon_instances,
            'marathon_cmd': controller.marathon_cmd,
            'description': controller.description,
            'envs': [
                {'key': env.key, 'value': env.value}
                for env in controller.env_variables.all()],
            'labels': [
                {'name': label.name, 'value': label.value}
                for label in controller.label_variables.all()],
            'links': [
                {'name': label.name, 'link': label.link}
                for label in controller.additional_link.all()]})
        return initial

    def get_success_url(self):
        return reverse("home")

    def form_valid(self, form):
        form.controller_form.instance.organization = active_organization(
            self.request)
        form.controller_form.instance.owner = self.request.user
        form.controller_form.instance.save()

        form.env_formset.instance = form.controller_form.instance
        form.link_formset.instance = form.controller_form.instance
        form.label_formset.instance = form.controller_form.instance

        response = super(ControllerCloneView, self).form_valid(form)
        tasks.start_new_controller.delay(form.controller_form.instance.id)
        return response


class ControllerEditView(ControllerViewMixin, UpdateView):
    form_class = ControllerFormHelper
    template_name = 'controller_edit.html'
    permissions = ['base.change_controller']

    def get_queryset(self):
        return self.get_controllers_queryset(self.request)

    def get_object(self):
        controller = get_object_or_404(
            Controller, pk=self.kwargs.get('controller_pk'))

        if self.request.user.is_superuser:
            return controller
        elif controller.organization:
            org = Organization.objects.for_user(self.request.user).filter(
                pk=controller.organization.id).first()
            if org and org.has_perms(
                    self.request.user, ['base.change_controller']):
                return controller
        raise HttpResponseNotFound()

    def get_success_url(self):
        return reverse("home")

    def form_valid(self, form):
        response = super(ControllerEditView, self).form_valid(form)
        tasks.update_marathon_app.delay(form.instance.id)
        messages.info(
            self.request, '%s app update requested.' % form.instance.app_id)
        return response


class AppLogView(ControllerViewMixin, TemplateView):
    template_name = 'app_logs.html'

    def get_context_data(self, *args, **kwargs):
        context = super(AppLogView, self).get_context_data(*args, **kwargs)
        controller = get_object_or_404(
            self.get_controllers_queryset(self.request),
            pk=kwargs['controller_pk'])
        tasks = controller.infra_manager.get_controller_marathon_tasks()
        context.update({
            'controller': controller,
            'tasks': tasks,
            'task_ids': [t['id'].split('.', 1)[1] for t in tasks],
            'paths': ['stdout', 'stderr'],
            'offset': self.request.GET.get('offset'),
            'length': self.request.GET.get('length'),
        })
        return context


class MesosFileLogView(ControllerViewMixin, View):
    def get(self, request, controller_pk, task_id, path):
        controller = get_object_or_404(
            self.get_controllers_queryset(request),
            pk=controller_pk)
        length = request.GET.get('length', '')
        offset = request.GET.get('offset', '')
        if path not in ['stdout', 'stderr']:
            return HttpResponseNotFound('File not found.')

        # NOTE: I'm piecing together the app_id and task_id here
        #       so as to not need to expose both in the templates.
        task = controller.infra_manager.get_controller_task_log_info(
            '%s.%s' % (controller.app_id, task_id))
        file_path = os.path.join(task['task_dir'], path)

        internal_redirect_url = settings.MESOS_FILE_API_PATH % {
            'worker_host': task['task_host'],
            'api_path': ('download.json'
                         if request.GET.get('download')
                         else 'read.json'),
        }

        response = HttpResponse()
        response['X-Accel-Redirect'] = '%s?%s' % (
            internal_redirect_url, urllib.urlencode((
                ('path', os.path.join(settings.MESOS_LOG_PATH, file_path)),
                ('length', length),
                ('offset', offset),
            )))

        response['X-Accel-Buffering'] = 'no'
        return response


class ControllerRestartView(ControllerViewMixin, View):
    # TODO: Check user permissions

    def get(self, request, controller_pk):
        controller = get_object_or_404(Controller, pk=controller_pk)
        tasks.marathon_restart_app.delay(controller.id)
        messages.info(
            self.request, '%s app restart requested.' % controller.app_id)
        return redirect('home')


class ControllerDeleteView(ControllerViewMixin, View):
    permissions = ['base.change_controller']

    # TODO: Check user permissions

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ControllerDeleteView, self).dispatch(*args, **kwargs)

    def post(self, request, controller_pk):
        controller = get_object_or_404(Controller, pk=controller_pk)
        tasks.marathon_destroy_app.delay(controller.id)
        messages.info(
            self.request, '%s app delete requested.' % controller.app_id)
        return redirect('home')


class ControllerWebhookRestartView(View):
    """
    Unauthenticated webhook to restart an app.

    Technically, this is a 'URL capability'.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(
            ControllerWebhookRestartView, self).dispatch(*args, **kwargs)

    def get(self, request, controller_pk, token):
        return HttpResponseNotAllowed(['POST'])

    def post(self, request, controller_pk, token):
        controller = get_object_or_404(Controller, pk=controller_pk)
        if str(controller.webhook_token) != token:
            return HttpResponseNotFound()

        try:
            controller.marathon_restart_app()
        except exceptions.MarathonApiException:
            return HttpResponseServerError(
                json.dumps({'error': 'Restart failed.'}),
                content_type='application/json')
        return HttpResponse(json.dumps({}), content_type='application/json')
