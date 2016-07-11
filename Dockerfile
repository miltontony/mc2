FROM praekeltfoundation/python-base:alpine

RUN apk --no-cache add nginx redis libffi postgresql-dev

ENV PROJECT_ROOT /deploy/
ENV DJANGO_SETTINGS_MODULE mc2.settings
ENV MESOS_MARATHON_HOST http://servicehost:8080

WORKDIR /deploy/

COPY mc2 /deploy/mc2
COPY manage.py \
    requirements.txt \
    requirements-dev.txt \
    setup.py \
    README.rst \
    VERSION \
    docker/docker-entrypoint.sh \
        /deploy/

COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/mc2.nginx.conf /etc/nginx/conf.d/
COPY docker/supervisord.conf /etc/supervisord.conf
COPY docker/mc2.supervisor.conf /etc/supervisor/conf.d/

RUN pip install gunicorn supervisor "Django<1.9,>=1.8" \
    && pip install -e .

RUN mkdir -p /var/log/supervisor

EXPOSE 80
CMD ["/deploy/docker-entrypoint.sh"]
