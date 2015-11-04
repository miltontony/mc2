from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from unicoremc import views

urlpatterns = patterns(
    '',
    url(
        r'^$',
        views.HomepageView.as_view(),
        name='home'
    ),
    url(
        r'^login/$',
        TemplateView.as_view(template_name='unicoremc/login.html'),
        name='login'
    ),
    url(
        r'^logout/$',
        'django.contrib.auth.views.logout_then_login',
        name='logout'
    )
)
