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
        r'^googleanalytics/$',
        'unicoremc.views.manage_ga_view',
        name='manage_ga'
    ),
    url(
        r'^googleanalytics/new/$',
        'unicoremc.views.manage_ga_new',
        name='manage_ga_new'
    ),
    url(
        r'^new/create/$',
        'unicoremc.views.start_new_project',
        name='start_new_project'
    ),
    url(
        r'^advanced/(?P<project_id>\d+)/$',
        views.ProjectEditView.as_view(),
        name='advanced'),
    url(
        r'^advanced/(?P<project_id>\d+)/reset_hub_app_key/$',
        'unicoremc.views.reset_hub_app_key',
        name='reset-hub-app-key'),
    url(
        r'^logout/$',
        'django.contrib.auth.views.logout_then_login',
        name='logout'
    ),
    url(
        r'^repos/$',
        'unicoremc.views.get_all_repos',
        name='get_all_repos'
    ),
)
