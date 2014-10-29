from django.conf.urls import patterns, url
from unicoremc import views


urlpatterns = patterns(
    '',
    url(
        r'^$',
        'unicoremc.views.home',
        name='home'
    ),
    url(
        r'^new/$',
        'unicoremc.views.new_project_view',
        name='new_project'
    ),
    url(
        r'^new/create/$',
        'unicoremc.views.start_new_project',
        name='start_new_project'
    ),
    url(
        r'^progress/$',
        'unicoremc.views.projects_progress',
        name='projects_progress'
    ),
    url(
        r'^advanced/(?P<project_id>\d+)/$',
        views.ProjectEditView.as_view(),
        name='advanced'),
    url(
        r'^logout/$',
        'django.contrib.auth.views.logout_then_login',
        name='logout'
    ),
)
