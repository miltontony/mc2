from django.conf.urls import patterns, url

from mc2.controllers.freebasics import views


urlpatterns = patterns(
    '',
    url(
        r'^add/$',
        views.FreeBasicsControllerCreateView.as_view(),
        name='add'
    ),
    url(
        r'^(?P<controller_pk>\d+)/$',
        views.FreeBasicsControllerEditView.as_view(),
        name='edit'),
)
