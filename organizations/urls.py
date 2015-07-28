from django.conf.urls import patterns, url

from organizations import views


urlpatterns = patterns(
    '',
    url(
        r'^$',
        views.SelectOrganizationView.as_view(),
        name='select',
    ),
    url(
        r'^(?P<slug>\w+)/select/$',
        views.SelectActiveOrganizationView.as_view(),
        name='select-active',
    ),
    url(
        r'^(?P<slug>\w+)/$',
        views.EditOrganizationView.as_view(),
        name='edit',
    ),
)
