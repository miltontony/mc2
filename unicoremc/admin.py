# ensure celery autodiscovery runs
from djcelery import admin as celery_admin

from djcelery.models import (
    TaskState, WorkerState, PeriodicTask, IntervalSchedule, CrontabSchedule)

from django.contrib import admin
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

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
        return '<br/>'.join([r.base_url for r in obj.all_repos()])
    base_repo_url_list.allow_tags = True

    def repo_url_list(self, obj):
        def repo_url(repo):
            url = repo.url or '-'
            if repo.project_id != obj.pk:
                return '%s (<a href="%s">owner project</a>)' % (
                    url, reverse(
                        'admin:unicoremc_project_change',
                        args=(repo.project_id,)))
            return url
        return '<br/>'.join(map(repo_url, obj.all_repos()))
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
