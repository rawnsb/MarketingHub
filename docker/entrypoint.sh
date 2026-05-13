#!/bin/sh
set -e
python manage.py migrate --noinput
# Gather admin and app static assets into STATIC_ROOT for WhiteNoise + Gunicorn
python manage.py collectstatic --noinput
exec gunicorn project.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${GUNICORN_WORKERS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-120}"
