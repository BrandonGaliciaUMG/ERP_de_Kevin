#!/bin/sh
set -eu

is_true() {
    case "${1:-}" in
        1|true|True|TRUE|yes|Yes|YES|on|On|ON) return 0 ;;
        *) return 1 ;;
    esac
}

if [ "${DB_HOST:-}" ]; then
    echo "Waiting for database at ${DB_HOST}:${DB_PORT:-5432}..."
    python - <<'PY'
import os
import socket
import time

host = os.environ.get("DB_HOST")
port = int(os.environ.get("DB_PORT", "5432"))
wait_timeout = int(os.environ.get("DB_WAIT_TIMEOUT", "180"))
deadline = time.time() + wait_timeout
last_error = None

while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print("Database is reachable.")
            break
    except OSError as exc:
        last_error = exc
        print(f"Database not ready yet: {exc}", flush=True)
        time.sleep(3)
else:
    raise SystemExit(
        f"Database {host}:{port} was not reachable in {wait_timeout} seconds. "
        f"Last error: {last_error}"
    )
PY
fi

if is_true "${RUN_MIGRATIONS:-True}"; then
    echo "Applying migrations..."
    python manage.py migrate --noinput
fi

if is_true "${RUN_COLLECTSTATIC:-False}"; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

if is_true "${RUN_SEED:-False}"; then
    SHOULD_SEED=1
    if is_true "${SEED_ONLY_IF_EMPTY:-True}"; then
        SHOULD_SEED="$(python - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.apps import apps

Cliente = apps.get_model("clientes", "Cliente")
print(0 if Cliente.objects.exists() else 1)
PY
)"
    fi

    if [ "$SHOULD_SEED" = "1" ]; then
        echo "Creating development users and seed data..."
        python manage.py seed \
            --clients "${SEED_CLIENTS:-20}" \
            --products "${SEED_PRODUCTS:-30}" \
            --orders "${SEED_ORDERS:-20}" \
            --sales "${SEED_SALES:-10}" \
            --claims "${SEED_CLAIMS:-10}"
    else
        echo "Seed data already exists; skipping. Set SEED_ONLY_IF_EMPTY=False to force it."
    fi
fi

exec "$@"
