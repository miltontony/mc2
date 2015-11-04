from django.conf.urls import patterns, url

from controllers.base import views


urlpatterns = patterns(
    '',
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