from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from unicoremc import views


urlpatterns = patterns(
    '',
    url(
        r'^$',
        views.HomepageView.as_view(),
        name='home'
    ),
    url(
        r'^login/$',
        TemplateView.as_view(template_name='unicoremc/login.html'),
        name='login'
    ),
    url(
        r'^new/$',
        views.NewProjectView.as_view(),
        name='new_project'
    ),
    url(
        r'^health/$',
        views.HealthCheckView.as_view(),
        name='health_check'
    ),
    url(
        r'^googleanalytics/$',
        views.ManageGAView.as_view(),
        name='manage_ga'
    ),
    url(
        r'^advanced/(?P<project_id>\d+)/$',
        views.ProjectEditView.as_view(),
        name='advanced'),
    url(
        r'^restart/(?P<project_id>\d+)/$',
        views.ProjectRestartView.as_view(),
        name='restart'),
    url(
        r'^logs/(?P<project_id>\d+)/$',
        views.AppLogView.as_view(),
        name='logs'),
    url(
        r'^logs/(?P<project_id>\d+)/(?P<task_id>[\w\.\-]+)/(?P<path>(stderr|stdout))/$',  # noqa
        views.AppEventSourceView.as_view(), name='logs_event_source'),
    url(
        r'^advanced/(?P<project_id>\d+)/reset_hub_app_key/$',
        views.ResetHubAppKeyView.as_view(),
        name='reset-hub-app-key'),
    url(
        r'^logout/$',
        'django.contrib.auth.views.logout_then_login',
        name='logout'
    ),
    url(
        r'^repos/$',
        'unicoremc.views.repos_json',
        name='repos_json'
    ),
    url(
        r'^teams/$',
        'unicoremc.views.teams_json',
        name='teams_json'
    ),
    url(
        r'^health/(?P<project_id>\d+)/$',
        'unicoremc.views.health_json',
        name='health_json'
    ),
    url(
        r'^exists/(?P<project_id>\d+)/$',
        'unicoremc.views.update_marathon_exists_json',
        name='update_marathon_exists_json'
    )
)
