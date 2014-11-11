#!/bin/bash

cp -a $REPO ./build/

${PIP} install -r $REPO/requirements.txt

# ensure these dependencies are always updated in the sideloader workspace
${PIP} uninstall elastic-git -y; ${PIP} install elastic-git
${PIP} uninstall unicore-cms -y; ${PIP} install unicore-cms
