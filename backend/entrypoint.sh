#!/bin/sh
set -eu

set +e
echo "Waiting for postgres..."
while ! nc -z "$DATABASE_HOST" "$DATABASE_PORT"; do
  sleep 0.1
done
echo "PostgreSQL started"
set -e

if [ "$MODE" = "production" ]; then
  ./manage.py collectstatic --noinput --clear
fi

./manage.py migrate --noinput

exec "$@"
