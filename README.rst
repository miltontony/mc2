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

Because this system uses GitHub with OAuth2 for authentication there are a few
steps one needs to complete in order to get a working system:

Create a super user::

    (ve)$ ve/bin/django-admin createsuperuser

Start the application on local address ``127.0.0.1:8000``::

    (ve)$ ve/bin/django-admin runserver

OAuth works with HTTP based callbacks & token exchange, for this to work our
local server needs to be reachable on the Internet. Ngrok_ is a great utility
that allows for this. Follow the installation instructions on the Ngrok_
website for your operating system. Once installed run::

    $ ngrok 8000

This will generate a random ``ngrok.com`` subdomain for you on which your
local server will be reachable. The random subdomain address is useful for
adhoc testing but we would recommend you use something predictable. This can
be done using the ``-subdomain`` command line argument::

    $ ngrok -subdomain mytestingtunnel 8000

Next you need to generate a pair of secret keys for OAuth in your GitHub
account. You can do this at https://github.com/settings/applications/new:

.. image:: http://note.io/1s0ZMdb
    :align: center

Once saved, GitHub will have generated the unique keys you will need to
complete the OAuth setup:

.. image:: http://note.io/1Aq99U8
    :align: center

You can specify the following ``environment variables`` to configure the app:

.. code-block:: python

    # Django settings
    SECRET_KEY
    PROJECT_ROOT
    DATABASE_URL

    # Mesos Settings
    MESOS_DEFAULT_MEMORY_ALLOCATION
    MESOS_MARATHON_HOST
    MESOS_HTTP_PORT
    MESOS_DEFAULT_CPU_SHARE
    MESOS_DEFAULT_INSTANCES

    # Log Driver settings
    LOGDRIVER_PATH
    LOGDRIVER_BACKLOG

    # Sentry configuration
    RAVEN_DSN
    RAVEN_CONFIG

    # Social Auth
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET

Once all this is done visit Mission Control via your
custom http://mytestingtunnel.ngrok.com tunnel and sign-up via GitHub.

You'll be greeted with an empty page since no applications have been created
yet. Only Django ``superusers`` are allowed to create new applications.
You'll need to login into the Django admin page as the superuser you created
earlier and promote the account created via GitHub to being a super user
to expose the application creation features.

.. _Ngrok: http://www.ngrok.com/
