#!/bin/sh
set -e

python manage.py migrate --noinput

exec gunicorn {{ cookiecutter.core_name }}.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --access-logfile - \
    --error-logfile -
