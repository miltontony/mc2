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
        r'^(?P<slug>\w+)/$',
        views.OrganizationActionsView.as_view(),
        name='admin',
    ),
    url(
        r'^(?P<slug>\w+)/edit/$',
        views.OrganizationEditView.as_view(),
        name='edit',
    )
)
