#!/bin/sh
# Enhanced entrypoint.sh for Django + PostgreSQL in production/development
set -eu

# Color output for logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo "${GREEN}✓${NC} $1"
}

log_warn() {
    echo "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo "${RED}✗${NC} $1" >&2
}

is_true() {
    case "${1:-}" in
        1|true|True|TRUE|yes|Yes|YES|on|On|ON) return 0 ;;
        *) return 1 ;;
    esac
}

debug_log() {
    if is_true "${DEBUG_DB_WAIT:-False}"; then
        echo "${YELLOW}[db-debug]${NC} $1"
    fi
}

# ============================================================================
# STEP 1: Wait for Database
# ============================================================================

if [ "${DB_HOST:-}" ]; then
    log_info "Waiting for database at ${DB_HOST}:${DB_PORT:-5432}..."
    debug_log "DEBUG_DB_WAIT enabled"
    debug_log "DB_HOST=${DB_HOST} DB_PORT=${DB_PORT:-5432} DB_WAIT_TIMEOUT=${DB_WAIT_TIMEOUT:-180}"
    
    python - <<'PY'
import os
import socket
import sys
import time
import traceback

host = os.environ.get("DB_HOST")
port = int(os.environ.get("DB_PORT", "5432"))
wait_timeout = int(os.environ.get("DB_WAIT_TIMEOUT", "180"))
debug = os.environ.get("DEBUG_DB_WAIT", "False").strip().lower() in {"1", "true", "yes", "on"}
deadline = time.time() + wait_timeout
last_error = None

def debug_print(message):
    if debug:
        print(f"[db-debug] {message}", flush=True)

debug_print(f"Resolving host: {host}")
try:
    infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    debug_print(f"getaddrinfo returned {len(infos)} result(s)")
    for info in infos:
        debug_print(f"addrinfo={info}")
except OSError as exc:
    debug_print(f"DNS resolution failed immediately: {exc}")

while time.time() < deadline:
    try:
        debug_print(f"Attempting TCP connection to {host}:{port}")
        with socket.create_connection((host, port), timeout=2):
            print("✓ Database is reachable.", flush=True)
            sys.exit(0)
    except OSError as exc:
        last_error = exc
        elapsed = int(time.time() - (deadline - wait_timeout))
        remaining = int(deadline - time.time())
        print(f"⏳ Database not ready yet: {exc} (elapsed: {elapsed}s, remaining: {remaining}s)", flush=True)
        debug_print(f"Exception type: {type(exc).__name__}")
        debug_print(f"Exception args: {exc.args}")
        debug_print(f"Traceback: {traceback.format_exc().strip()}")
        time.sleep(3)

print(f"✗ Database {host}:{port} was not reachable in {wait_timeout} seconds.", flush=True)
print(f"Last error: {last_error}", flush=True)
sys.exit(1)
PY
    
    if [ $? -ne 0 ]; then
        log_error "Database connection failed. Aborting startup."
        exit 1
    fi
else
    log_warn "DB_HOST not set. Using SQLite (development mode)."
fi

# ============================================================================
# STEP 2: Run Migrations
# ============================================================================

if is_true "${RUN_MIGRATIONS:-True}"; then
    log_info "Applying database migrations..."
    
    if python manage.py migrate --noinput; then
        log_info "Migrations applied successfully"
    else
        log_error "Migration failed. Check database connection and migrations."
        exit 1
    fi
else
    log_warn "Skipping migrations (RUN_MIGRATIONS=False)"
fi

# ============================================================================
# STEP 3: Collect Static Files
# ============================================================================

if is_true "${RUN_COLLECTSTATIC:-True}"; then
    log_info "Collecting static files..."
    
    if python manage.py collectstatic --noinput --clear; then
        log_info "Static files collected successfully"
    else
        log_error "Collectstatic failed. Check file permissions and disk space."
        exit 1
    fi
else
    log_warn "Skipping collectstatic (RUN_COLLECTSTATIC=False)"
fi

# ============================================================================
# STEP 4: Create Default Admin User
# ============================================================================

log_info "Ensuring admin user exists..."

python manage.py shell << 'CREATE_ADMIN'
from django.contrib.auth.models import User
import os

if not User.objects.filter(username='admin').exists():
    admin_password = os.environ.get('ADMIN_PASSWORD', 'changeme')
    User.objects.create_superuser('admin', 'admin@example.com', admin_password)
    print(f"✓ Admin user created (username: admin)")
else:
    print("✓ Admin user already exists")
CREATE_ADMIN

# ============================================================================
# STEP 5: Final Verification
# ============================================================================

log_info "Running final health checks..."

python manage.py check --deploy 2>/dev/null || {
    log_warn "Some deployment checks need attention (review above)"
}

log_info "All startup tasks completed successfully!"
log_info "Starting application server..."

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

# ============================================================================
# STEP 6: Fix Permissions and Switch User
# ============================================================================

log_info "Fixing directory permissions for django_user..."
chown -R 1000:1000 /app/staticfiles /app/media 2>/dev/null || {
    log_warn "Could not chown staticfiles/media (may already be owned by django_user)"
}

log_info "Switching to django_user and starting server..."
exec su django_user -c "exec $*"
