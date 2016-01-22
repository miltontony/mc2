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

Because this system uses Google Accounts with OAuth2 for authentication there are a few
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

    $ ngrok -subdomain mc2 8000

If you haven't already, create a Google Developer Project at
``https://console.developers.google.com/project`` .

.. image:: images/pic1.png
    :align: center

Next, navigate to ``https://console.developers.google.com/apis/credentials`` ,
select the 'OAuth Consent Screen', choose a product name and save.

.. image:: images/pic2.png
    :align: center

Then select "New credentials" and select "OAuth Client ID". Then enter the
necessary information

.. image:: images/pic3.png
    :align: center

Once saved, Google will have generated the unique keys you will need to
complete the OAuth setup:

.. image:: images/pic4.png
    :align: center

For quick setup, you would then enter the following::

    (ve)$ export SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="647082549192-142tni49187fck8i2n1p0ptjofihd1k4.apps.googleusercontent.com"
    (ve)$ export SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET="mJG2Qgbsmwal8MdCeP_7x_S6D"

Your Google OAuth setup should now be configured.

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

Once all this is done visit MC2 via your
custom http://mc2.ngrok.com tunnel and sign-up via Google.

You'll be greeted with an empty page since no applications have been created
yet. Only Django ``superusers`` are allowed to create new applications.
You'll need to login into the Django admin page as the superuser you created
earlier and promote the account created via GitHub to being a super user
to expose the application creation features.

.. _Ngrok: http://www.ngrok.com/
