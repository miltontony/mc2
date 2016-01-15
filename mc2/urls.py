from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.contrib import admin

from mc2 import views

admin.autodiscover()


urlpatterns = patterns(
    '',
    url(
        r'^$',
        views.HomepageView.as_view(),
        name='home'
    ),
    url(
        r'^login/$',
        TemplateView.as_view(template_name='mc2/login.html'),
        name='login'
    ),
    url(
        r'^logout/$',
        'django.contrib.auth.views.logout_then_login',
        name='logout'
    ),
    url(
        r'^settings/update/$',
        login_required(views.UserSettingsView.as_view()),
        name='user_settings'
    ),
    url(r'^', include('mc2.controllers.urls')),
    url(
        r'^organizations/',
        include('mc2.organizations.urls', namespace='organizations')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(
        r'^social/',
        include('social.apps.django_app.urls', namespace='social')),
)
