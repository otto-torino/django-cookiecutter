#!/bin/sh
set -eu

run_as_django() {
  if command -v gosu >/dev/null 2>&1 && [ "$(id -u)" = "0" ]; then
    gosu django "$@"
  else
    "$@"
  fi
}

start_postgres() {
  data_dir="${POSTGRES_DATA_DIR:-/var/lib/postgresql/data}"
  db_name="${DB_NAME:?Set DB_NAME}"
  db_user="${DB_USER:?Set DB_USER}"
  db_password="${DB_PASSWORD:?Set DB_PASSWORD}"
  db_port="${DB_PORT:-5432}"

  mkdir -p "$data_dir" /run/postgresql
  chown -R postgres:postgres "$data_dir" /run/postgresql

  if [ ! -s "$data_dir/PG_VERSION" ]; then
    gosu postgres initdb -D "$data_dir" --auth-local=trust --auth-host=scram-sha-256
  fi

  gosu postgres pg_ctl -D "$data_dir" \
    -o "-c listen_addresses=127.0.0.1 -p $db_port" \
    -w start

  gosu postgres psql \
    -v ON_ERROR_STOP=1 \
    -v db_name="$db_name" \
    -v db_user="$db_user" \
    -v db_password="$db_password" \
    --dbname postgres <<'SQL'
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'db_user', :'db_password')
WHERE NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = :'db_user')\gexec

SELECT format('ALTER ROLE %I WITH LOGIN PASSWORD %L', :'db_user', :'db_password')\gexec

SELECT format('CREATE DATABASE %I OWNER %I', :'db_name', :'db_user')
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = :'db_name')\gexec
SQL
}

export DB_HOST=127.0.0.1
export DB_PORT="${DB_PORT:-5432}"
start_postgres

if [ -n "${DB_HOST:-}" ]; then
  run_as_django python - <<'PY'
import os
import socket
import time

host = os.environ["DB_HOST"]
port = int(os.environ.get("DB_PORT", "5432"))
deadline = time.time() + int(os.environ.get("DB_WAIT_TIMEOUT", "60"))

while True:
    try:
        with socket.create_connection((host, port), timeout=3):
            break
    except OSError:
        if time.time() >= deadline:
            raise
        time.sleep(1)
PY
fi

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
  run_as_django python manage.py migrate --noinput
fi

{% if cookiecutter.use_translations == 'y' -%}
if [ "${SYNC_TRANSLATION_FIELDS:-1}" = "1" ]; then
  run_as_django python manage.py sync_translation_fields --noinput
fi
{% endif -%}

if [ "${COLLECTSTATIC_ON_STARTUP:-1}" = "1" ]; then
  run_as_django python manage.py collectstatic --noinput
fi

if [ "$#" -eq 0 ] || [ "$1" = "serve" ]; then
  exec gosu django gunicorn core.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${GUNICORN_WORKERS:-4}" \
    --access-logfile - \
    --error-logfile -
fi

exec "$@"
