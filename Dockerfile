FROM praekeltfoundation/python-base:alpine

RUN apk --no-cache add nginx redis libffi postgresql-dev

ENV PROJECT_ROOT /deploy/
ENV DJANGO_SETTINGS_MODULE mc2.settings
ENV MESOS_MARATHON_HOST http://servicehost:8080

WORKDIR /deploy/

COPY mc2 /deploy/mc2
ADD manage.py /deploy/
ADD requirements.txt /deploy/
ADD requirements-dev.txt /deploy/
ADD setup.py /deploy/
ADD README.rst /deploy/
ADD VERSION /deploy/
ADD docker/docker-entrypoint.sh /deploy/
ADD docker/nginx.conf /etc/nginx/nginx.conf
ADD docker/mc2.nginx.conf /etc/nginx/conf.d/
ADD docker/supervisord.conf /etc/
ADD docker/mc2.supervisor.conf /etc/supervisor/conf.d/

RUN pip install gunicorn supervisor "Django<1.9,>=1.8" \
    && pip install -e .

RUN mkdir -p /etc/supervisor/conf.d/
RUN mkdir -p /var/log/supervisor

RUN chmod +x /deploy/docker-entrypoint.sh

EXPOSE 80
CMD ["/deploy/docker-entrypoint.sh"]
