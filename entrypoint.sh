#!/bin/bash

# Creating diretories here instead of in Dockerfile for backwards compatibility
mkdir /home/app/web/writable/media
mkdir /home/app/web/writable/log

if [ "$RUN_MIGRATE" != "no" ]; then
    python manage.py migrate --noinput;
fi

if [ "$RUN_COLLECTSTATIC" != "no" ]; then
    python manage.py collectstatic --noinput;
fi

gunicorn ${WSGI_APP} --bind 0.0.0.0:${DJANGO_PORT} \
                     --log-level debug \
                     --workers=${NUMBER_OF_WORKERS:-4} \
                     --timeout 900