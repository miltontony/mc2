# ensure celery autodiscovery runs
from djcelery import admin as celery_admin  # noqa

from djcelery.models import (
    TaskState, WorkerState, PeriodicTask, IntervalSchedule, CrontabSchedule)

from django.contrib import admin
from django.contrib.sites.models import Site

from mc2.controllers.base.models import Controller


class ControllerAdmin(admin.ModelAdmin):
    search_fields = ('state', 'name')
    list_filter = ('state',)
    list_display = ('name', 'state', 'organization')
    list_editable = ('organization',)
    readonly_fields = ('state', 'owner')

admin.site.register(Controller, ControllerAdmin)

# remove celery from admin
admin.site.unregister(Site)
admin.site.unregister(TaskState)
admin.site.unregister(WorkerState)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(PeriodicTask)
