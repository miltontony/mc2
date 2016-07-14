#!/bin/sh

set -e

echo "setting up the database"
django-admin.py migrate
django-admin.py collectstatic --noinput

echo "from django.contrib.auth.models import User
if not User.objects.filter(username='admin').count():
    User.objects.create_superuser('admin', 'admin@example.com', 'pass')
" | django-admin.py shell

echo "=> Starting Supervisord"
supervisord -c /etc/supervisord.conf
