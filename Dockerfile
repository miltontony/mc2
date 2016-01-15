FROM python:2.7.10

RUN apt-get update && apt-get install -y \
	redis-server nginx

ENV PROJECT_ROOT /deploy/
ENV DJANGO_SETTINGS_MODULE mc2.settings
ENV MC2_VERSION 3.0.5
ENV MESOS_MARATHON_HOST http://servicehost:8080

WORKDIR /deploy/

RUN pip install gunicorn
RUN pip install supervisor
RUN pip install "Django<1.9,>=1.8"
RUN pip install mission-control2==$MC2_VERSION


RUN rm /etc/nginx/sites-enabled/default

ADD docker/docker-entrypoint.sh /deploy/
ADD docker/mc2.nginx.conf /etc/nginx/sites-enabled/

RUN mkdir -p /etc/supervisor/conf.d/
RUN mkdir -p /var/log/supervisor

ADD docker/supervisord.conf /etc/
ADD docker/mc2.supervisor.conf /etc/supervisor/conf.d/

RUN chmod +x /deploy/docker-entrypoint.sh

RUN django-admin.py migrate
RUN django-admin.py collectstatic --noinput

EXPOSE 80
ENTRYPOINT ["/deploy/docker-entrypoint.sh"]
