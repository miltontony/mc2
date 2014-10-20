from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(
        r'^$',
        'unicoremc.views.home',
        name='home'
    ),
    url(
        r'^new/$',
        'unicoremc.views.new_project_view',
        name='new_project'
    ),
    url(
        r'^new/sleep/$',
        'unicoremc.views.test_ajax_function',
        name='new_project_sleep'
    ),
    url(
        r'^logout/$',
        'django.contrib.auth.views.logout_then_login',
        name='logout'
    ),
)
