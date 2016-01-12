manage="${VENV}/bin/python ${INSTALLDIR}/${REPO}/manage.py"

$manage migrate --noinput --no-initial-data
$manage collectstatic --noinput

sudo supervisorctl restart unicore_mc unicore_mc_celery
