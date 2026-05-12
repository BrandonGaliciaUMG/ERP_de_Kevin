# Guía de Deployment en Dokploy - ERP de Kevin

## 📋 Análisis de la Configuración Actual

### Estado Positivo ✅
1. **Docker multi-etapa bien configurado**: Usa `python:3.11-slim` con usuario no-root (`django_user`)
2. **Health check en la BD**: Verifica que PostgreSQL esté listo antes de ejecutar la app
3. **Variables de entorno centralizadas**: Usa `.env` para desarrollo y variables de entorno en Dokploy
4. **Entrypoint inteligente**: Espera a la base de datos y ejecuta migraciones automáticamente
5. **Gestión de archivos estáticos**: Usa WhiteNoise para servir assets sin nginx extra

---

## ⚠️ Problemas Críticos Identificados

### 1. **Comando Incorrecto en docker-compose.yml**
```yaml
command: python manage.py runserver 0.0.0.0:8000  # ❌ DEV ONLY
```

**Problema**: En Dokploy (producción), esto causará:
- Servidor de desarrollo NO apto para producción
- Bajo rendimiento
- Fallos bajo carga

**Solución**: El Dockerfile usa `gunicorn` (correcto), pero docker-compose lo sobrescribe.

---

### 2. **Entrypoint Incompleto**
El script `entrypoint.sh` NO ejecuta el seed de datos en Dokploy.

**Problema**: Las variables `RUN_SEED`, `SEED_CLIENTS`, etc. están en `docker-compose.yml` pero no se usan en el entrypoint.

**Solución**: Agregar seed opcional al entrypoint.

---

### 3. **Variables de Entorno Inseguras en Producción**
```yaml
SECRET_KEY: ${DOCKER_SECRET_KEY:-django-insecure-dev-docker-change-me}  # ❌ Default inseguro
DEBUG: ${DOCKER_DEBUG:-True}  # ❌ Nunca True en producción
ALLOWED_HOSTS: localhost,127.0.0.1,0.0.0.0  # ❌ No incluye tu dominio
```

---

### 4. **Sin Manejo de Volúmenes Persistentes en Dokploy**
- Archivos subidos al `MEDIA_ROOT` se pierden al reiniciar
- Necesita volumen persistente en Dokploy

---

### 5. **Sin Backups de Base de Datos**
- PostgreSQL en Docker pierde datos si se elimina el contenedor
- Dokploy no hace backup automático por defecto

---

## 🔧 Recomendaciones por Severidad

### CRÍTICO (Hacer Primero)

#### 1️⃣ Crear `.env.production` con valores reales
```bash
# .env.production (NO subir a git)
SECRET_KEY=tu-clave-secreta-generada-aleatoriamente
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
POSTGRES_DB=erp_ventas_prod
POSTGRES_USER=erp_user
POSTGRES_PASSWORD=contraseña-fuerte-aleatoria
DB_HOST=postgres  # nombre del servicio en Dokploy
DB_PORT=5432
CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_PROXY_SSL_HEADER=True
```

#### 2️⃣ Crear `docker-compose.production.yml`
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: erp_ventas_db_prod
    restart: always
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8"
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
      - ./backups:/backups  # Para backups automáticos
    ports:
      - "5432:5432"  # Solo si acceso local es necesario
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build: .
    container_name: erp_ventas_web_prod
    restart: always
    environment:
      SECRET_KEY: ${SECRET_KEY}
      DEBUG: ${DEBUG}
      ALLOWED_HOSTS: ${ALLOWED_HOSTS}
      DB_ENGINE: django.db.backends.postgresql
      DB_NAME: ${POSTGRES_DB}
      DB_USER: ${POSTGRES_USER}
      DB_PASSWORD: ${POSTGRES_PASSWORD}
      DB_HOST: db
      DB_PORT: 5432
      DB_WAIT_TIMEOUT: 180
      CSRF_TRUSTED_ORIGINS: ${CSRF_TRUSTED_ORIGINS}
      SECURE_PROXY_SSL_HEADER: True
      SESSION_COOKIE_SECURE: True
      CSRF_COOKIE_SECURE: True
      SECURE_SSL_REDIRECT: True
      SECURE_HSTS_SECONDS: 31536000
      SECURE_HSTS_INCLUDE_SUBDOMAINS: True
      SECURE_HSTS_PRELOAD: True
      RUN_COLLECTSTATIC: True
      RUN_MIGRATIONS: True
      RUN_SEED: False  # ❌ NO ejecutar seed en producción
    volumes:
      - media_data:/app/media  # Volumen persistente para uploads
      - static_data:/app/staticfiles
    expose:
      - "8000"
    depends_on:
      db:
        condition: service_healthy

volumes:
  postgres_data_prod:
    driver: local
  media_data:
    driver: local
  static_data:
    driver: local
```

#### 3️⃣ Actualizar `entrypoint.sh` para producción
```bash
#!/bin/sh
set -eu

is_true() {
    case "${1:-}" in
        1|true|True|TRUE|yes|Yes|YES|on|On|ON) return 0 ;;
        *) return 1 ;;
    esac
}

# Esperar a la base de datos
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
            print("✓ Database is reachable.", flush=True)
            break
    except OSError as exc:
        last_error = exc
        print(f"⏳ Database not ready yet: {exc}", flush=True)
        time.sleep(3)
else:
    raise SystemExit(
        f"✗ Database {host}:{port} was not reachable in {wait_timeout} seconds. "
        f"Last error: {last_error}"
    )
PY
fi

# Aplicar migraciones
if is_true "${RUN_MIGRATIONS:-True}"; then
    echo "📦 Applying migrations..."
    python manage.py migrate --noinput || {
        echo "✗ Migration failed!"
        exit 1
    }
fi

# Recolectar archivos estáticos
if is_true "${RUN_COLLECTSTATIC:-True}"; then
    echo "📂 Collecting static files..."
    python manage.py collectstatic --noinput --clear || {
        echo "✗ Collectstatic failed!"
        exit 1
    }
fi

# Ejecutar seed SOLO si está habilitado (desarrollo/testing)
if is_true "${RUN_SEED:-False}"; then
    if is_true "${SEED_ONLY_IF_EMPTY:-True}"; then
        # Verificar si hay usuarios
        python manage.py shell -c "from django.contrib.auth.models import User; exit(0 if User.objects.exists() else 1)" 2>/dev/null && {
            echo "⏭️  Database already seeded, skipping..."
        } || {
            echo "🌱 Seeding database..."
            python manage.py shell << 'SEED_SCRIPT'
# Script de seed aquí
SEED_SCRIPT
        }
    else
        echo "🌱 Seeding database (forced)..."
        python manage.py shell << 'SEED_SCRIPT'
# Script de seed aquí
SEED_SCRIPT
    fi
fi

# Crear usuario admin si no existe
echo "👤 Ensuring admin user exists..."
python manage.py shell <<'ADMIN'
from django.contrib.auth.models import User
import os

if not User.objects.filter(username='admin').exists():
    admin_pass = os.environ.get('ADMIN_PASSWORD', 'changeme')
    User.objects.create_superuser('admin', 'admin@example.com', admin_pass)
    print(f"✓ Admin user created (password: {admin_pass})")
else:
    print("✓ Admin user already exists")
ADMIN

echo "✓ All startup tasks completed!"
