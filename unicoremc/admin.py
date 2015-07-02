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
        'application_type', 'country', 'state', 'base_repo_url', 'repo_url')
    readonly_fields = (
        'application_type', 'base_repo_url', 'country', 'repo_url', 'owner',
        'available_languages')


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
