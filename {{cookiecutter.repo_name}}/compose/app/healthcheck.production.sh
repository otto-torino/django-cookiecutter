#!/bin/sh
set -eu

pg_isready \
  --host "${DB_HOST:-127.0.0.1}" \
  --port "${DB_PORT:-5432}" \
  --username "${DB_USER:?Set DB_USER}" \
  --dbname "${DB_NAME:?Set DB_NAME}" \
  --quiet

python - <<'PY'
import os
import socket

with socket.create_connection(("127.0.0.1", int(os.environ.get("PORT", "8000"))), timeout=3):
    pass
PY
