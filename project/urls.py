from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

from adminplus.sites import AdminSitePlus

admin.site = AdminSitePlus()
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', RedirectView.as_view(url='/')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^', include(admin.site.urls)),
)
