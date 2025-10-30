#!/bin/sh

# Wait for the database to be ready
# This is a simple loop; for robust production, consider using a tool like wait-for-it.sh
echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

python manage.py migrate

exec "$@"