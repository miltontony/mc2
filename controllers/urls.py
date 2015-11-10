from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(
        r'^base/',
        include('controllers.base.urls', namespace='base')),
    url(
        r'^docker/',
        include('controllers.docker.urls', namespace='controllers.docker')),
)
