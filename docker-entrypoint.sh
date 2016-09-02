#!/bin/bash
python manage.py migrate # Apply database migrations
python manage.py graphql_schema --out ./public/schema.json

# Prepare log files and start outputting logs to stdout
touch /var/log/gunicorn.log
touch /var/log/access.log
tail -n 0 -f /var/log/gunicorn.log /var/log/access.log &

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn origem.wsgi:application \
    --name origem \
    --bind 0.0.0.0:9090 \
    --workers 2 \
    --log-level=info \
    --log-file=/var/log/gunicorn.log \
    --access-logfile=/var/log/access.log \
    "$@"
