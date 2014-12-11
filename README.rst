Unicore Mission Control
=======================

A project launcher for Universal Core

Installation
------------
To install using a terminal::

    $ virtualenv ve
    $ source ve/bin/activate
    (ve)$ pip install -e .
    $ ./manage.py syncdb --migrate --noinput

Running
-------
The default runner is on port ``8000``::

    $ ./manage.py runserver
