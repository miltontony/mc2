from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(
        r'^base/',
        include('mc2.controllers.base.urls', namespace='base')),
    url(
        r'^docker/',
        include(
            'mc2.controllers.docker.urls', namespace='controllers.docker')),
)
