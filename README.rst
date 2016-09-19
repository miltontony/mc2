Mission Control
===============

A project launcher for Marathon

Installation
------------
To install using a terminal::

    $ virtualenv ve
    $ source ve/bin/activate
    (ve)$ pip install mission-control2
    (ve)$ export DJANGO_SETTINGS_MODULE="mc2.settings"
    (ve)$ ve/bin/django-admin migrate --noinput

Running
-------

Because this system uses Google Accounts with OAuth2 for authentication, in dev, it's easiest to just login using your superuser:

Create a super user::

    (ve)$ ./manage.py createsuperuser

Start the application on local address ``127.0.0.1:8000``::

    (ve)$ DEBUG=True ./manage.py runserver
