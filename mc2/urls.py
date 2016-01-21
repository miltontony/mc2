from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.contrib.auth.views import password_reset
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
        r'^accounts/password/reset/$', password_reset,
        {'template_name': 'password_reset_form.html'},
        name='password_change'),
    url(
        r'^accounts/password/reset/sent/$',
        'django.contrib.auth.views.password_reset_done',
        {'template_name': 'password_reset_done.html'},
        name='password_reset_done'),

    url(r'^login/?$', views.MC2LoginView.as_view(), name='login'),
    url(r'', include('mama_cas.urls')),
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
