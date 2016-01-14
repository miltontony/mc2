FROM python:2.7.10

RUN apt-get update && apt-get install -y \
	redis-server nginx

RUN service nginx start

ENV PROJECT_ROOT /deploy/
ENV DJANGO_SETTINGS_MODULE mc2.settings
ENV MC2_VERSION 3.0.5

WORKDIR /deploy/

RUN pip install gunicorn
RUN pip install supervisor
RUN pip install "Django<1.9,>=1.8"
RUN pip install mission-control2==$MC2_VERSION

ADD docker-entrypoint.sh /deploy/
RUN chmod +x /deploy/docker-entrypoint.sh

RUN django-admin.py migrate
RUN django-admin.py collectstatic --noinput

EXPOSE 80
ENTRYPOINT ["/deploy/docker-entrypoint.sh"]
