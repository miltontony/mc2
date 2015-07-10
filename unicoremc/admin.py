# ensure celery autodiscovery runs
from djcelery import admin as celery_admin

from djcelery.models import (
    TaskState, WorkerState, PeriodicTask, IntervalSchedule, CrontabSchedule)

from django.contrib import admin
from django.contrib.sites.models import Site

from unicoremc.models import Project, Localisation, AppType
from unicoremc.states import ProjectWorkflow

from ostinato.statemachine.forms import sm_form_factory


class ProjectAdmin(admin.ModelAdmin):
    form = sm_form_factory(ProjectWorkflow)

    search_fields = (
        'state', 'country', 'application_type__name',
        'application_type__title', 'application_type__project_type')
    list_filter = ('state', 'application_type')
    list_display = (
        'application_type', 'country', 'state', 'base_repo_url_list',
        'repo_url_list')
    readonly_fields = (
        'application_type', 'base_repo_url_list', 'country',
        'repo_url_list', 'owner', 'available_languages')

    def base_repo_url_list(self, obj):
        return '<br/>'.join(obj.base_repo_urls())
    base_repo_url_list.allow_tags = True

    def repo_url_list(self, obj):
        return '<br/>'.join(map(lambda url: url or '-', obj.repo_urls()))
    repo_url_list.allow_tags = True


admin.site.register(Localisation, admin.ModelAdmin)
admin.site.register(AppType, admin.ModelAdmin)
admin.site.register(Project, ProjectAdmin)

# remove celery from admin
admin.site.unregister(Site)
admin.site.unregister(TaskState)
admin.site.unregister(WorkerState)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(PeriodicTask)
