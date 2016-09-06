#!/bin/bash

cp -a $REPO ./build/

# ensure `praekelt-pyramid-celery` is removed from sideloader workspace
${PIP} uninstall praekelt-pyramid-celery -y

# install Django first - workaround for django-appregister: it tries to install the latest django
${PIP} install "Django<1.7"
${PIP} install -r $REPO/requirements.txt -U

# ensure these dependencies are always updated in the sideloader workspace
# ${PIP} uninstall elastic-git -y; ${PIP} install elastic-git
# ${PIP} uninstall unicore-cms -y; ${PIP} install unicore-cms
