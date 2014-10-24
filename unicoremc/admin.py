# ensure celery autodiscovery runs
from djcelery import admin as celery_admin

from djcelery.models import (
    TaskState, WorkerState, PeriodicTask, IntervalSchedule, CrontabSchedule)

from django.contrib import admin
from django.contrib.sites.models import Site

from unicoremc.models import Project, Localisation


class ProjectAdmin(admin.ModelAdmin):

    list_display = (
        'app_type', 'country', 'state', 'base_repo_url', 'repo_url')
    readonly_fields = (
        'app_type', 'base_repo_url', 'country', 'state', 'repo_url', 'owner',
        'available_languages')

admin.site.register(Localisation, admin.ModelAdmin)
admin.site.register(Project, ProjectAdmin)

# remove celery from admin
admin.site.unregister(Site)
admin.site.unregister(TaskState)
admin.site.unregister(WorkerState)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(PeriodicTask)
