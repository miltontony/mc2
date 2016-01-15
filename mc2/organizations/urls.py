from django.conf.urls import patterns, url

from mc2.organizations import views


urlpatterns = patterns(
    '',
    url(
        r'^(?P<slug>[\w-]+)/select/$',
        views.SelectActiveOrganizationView.as_view(),
        name='select-active',
    ),
    url(
        r'^deselect/$',
        views.DeselectActiveOrganizationView.as_view(),
        name='deselect-active',
    ),
    url(
        r'^(?P<slug>[\w-]+)/$',
        views.EditOrganizationView.as_view(),
        name='edit',
    ),
)
