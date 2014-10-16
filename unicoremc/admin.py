# ensure celery autodiscovery runs
from djcelery import admin as celery_admin

from djcelery.models import (
    TaskState, WorkerState, PeriodicTask, IntervalSchedule, CrontabSchedule)

from django.contrib import admin
from unicoremc.views import *

# remove celery from admin
admin.site.unregister(TaskState)
admin.site.unregister(WorkerState)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(PeriodicTask)
