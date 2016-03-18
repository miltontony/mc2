FROM praekeltfoundation/django-bootstrap
RUN DJANGO_SETTINGS_MODULE=mc2.build_settings django-admin compress && \
    DJANGO_SETTINGS_MODULE=mc2.build_settings django-admin collectstatic --noinput
ENV DJANGO_SETTINGS_MODULE="mc2.docker_settings" \
    APP_MODULE="mc2.wsgi:application"
