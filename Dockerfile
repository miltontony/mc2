FROM python:2.7.10

RUN apt-get update && apt-get install -y --no-install-recommends \
	redis-server && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

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
ADD docker/supervisord.conf /etc/
ADD docker/mc2.supervisor.conf /etc/supervisor/conf.d/

RUN pip install gunicorn supervisor "Django<1.9,>=1.8" && \
    pip install -e . && \
    rm -rf ~/.cache/pip

RUN mkdir -p /etc/supervisor/conf.d/
RUN mkdir -p /var/log/supervisor

RUN chmod +x /deploy/docker-entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/deploy/docker-entrypoint.sh"]
