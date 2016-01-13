FROM python:2.7.10

RUN apt-get update && apt-get install -y \
	redis-server

RUN virtualenv ./deploy/ve
RUN . ./deploy/ve/bin/activate
RUN pip install gunicorn
RUN pip install supervisor
RUN pip install "Django<1.9,>=1.8"
RUN pip install -U mission-control2
RUN PYTHONPATH=. django-admin.py migrate --settings=mc2.settings
ADD docker-entrypoint.sh ./deploy/
RUN chmod +x ./deploy/docker-entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["./deploy/docker-entrypoint.sh", "mc2", "mc2.wsgi", "8000"]
