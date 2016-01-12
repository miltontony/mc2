from django.conf.urls import patterns, url

from mc2.controllers.docker import views


urlpatterns = patterns(
    '',
    url(
        r'^add/$',
        views.DockerControllerCreateView.as_view(),
        name='add'
    ),
    url(
        r'^(?P<controller_pk>\d+)/$',
        views.DockerControllerEditView.as_view(),
        name='edit'),
)
