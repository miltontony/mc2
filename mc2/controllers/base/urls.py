from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import admin

from mc2.controllers.base import views

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(
        r'^$',
        login_required(
            TemplateView.as_view(template_name='home.html')),
        name='home'
    ),
    url(r'', include('mama_cas.urls')),
    url(
        r'^add/$',
        views.ControllerCreateView.as_view(),
        name='add'
    ),
    url(
        r'^(?P<controller_pk>\d+)/$',
        views.ControllerEditView.as_view(),
        name='edit'),
    url(
        r'^restart/(?P<controller_pk>\d+)/$',
        views.ControllerRestartView.as_view(),
        name='restart'),
    url(
        r'^delete/(?P<controller_pk>\d+)/$',
        views.ControllerDeleteView.as_view(),
        name='delete'),
    url(
        r'^logs/(?P<controller_pk>\d+)/$',
        views.AppLogView.as_view(),
        name='logs'),
    url(
        r'^logs/(?P<controller_pk>\d+)/(?P<task_id>[\w\.\-]+)/(?P<path>(stderr|stdout))/$',  # noqa
        views.AppEventSourceView.as_view(), name='logs_event_source'),
    url(
        r'^exists/(?P<controller_pk>\d+)/$',
        views.update_marathon_exists_json,
        name='update_marathon_exists_json'
    )
)
