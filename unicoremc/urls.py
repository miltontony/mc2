from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    '',
    url(
        r'^$',
        'unicoremc.views.home',
        name='home'
    ),
    url(
        r'^supervisor/$',
        'unicoremc.views.list_supervisor_configs_view',
        name='supervisor_list'
    ),
    url(
        r'^supervisor/detail/$',
        'unicoremc.views.supervisor_config_view',
        name='supervisor_detail'
    ),
    url(
        r'^nginx/$',
        'unicoremc.views.list_nginx_configs_view',
        name='nginx_list'
    ),
    url(
        r'^nginx/detail/$',
        'unicoremc.views.nginx_config_view',
        name='nginx_detail'
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
