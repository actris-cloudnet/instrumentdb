#!/bin/sh
set -eu

SERVICE=$(echo "$DATABASE_SERVICE" | tr '[:lower:]' '[:upper:]')
HOST=$(eval "echo \$${SERVICE}_SERVICE_HOST")
PORT=$(eval "echo \$${SERVICE}_SERVICE_PORT")

set +e
echo "Waiting for postgres..."
while ! nc -z "$HOST" "$PORT"; do
  sleep 0.1
done
echo "PostgreSQL started"
set -e

if [ "$DEBUG" != "1" ]; then
  ./manage.py collectstatic --noinput --clear
fi

./manage.py migrate --noinput

exec "$@"
