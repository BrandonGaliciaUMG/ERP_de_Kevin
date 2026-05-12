# Configuración Recomendada para Dokploy

## Estructura en Dokploy

```
Project: ERP de Kevin
├── Service: web (Django)
│   ├── Port: 8000 (internal)
│   ├── Expose: Port 80 → 8000 (HTTP - redirigido a HTTPS)
│   ├── Environment: [Ver .env.production]
│   └── Volumes:
│       ├── /app/media → media-persistent
│       └── /app/staticfiles → static-persistent
│
└── Service: postgres (PostgreSQL 15)
    ├── Port: 5432 (internal)
    ├── Environment: [Credenciales]
    └── Volumes: /var/lib/postgresql/data → postgres-data-prod
```

---

## Variables de Entorno para Dokploy

Crear en Dokploy → Project → Web Service → Environment Variables:

```
# === SEGURIDAD ===
SECRET_KEY=django-insecure-tu-clave-aleatoria-aqui  # USAR COMANDO ABAJO
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# === BASE DE DATOS ===
DB_ENGINE=django.db.backends.postgresql
DB_NAME=erp_ventas_prod
DB_USER=erp_user
DB_PASSWORD=tu-contrasena-fuerte-aqui
DB_HOST=postgres-service  # Nombre del servicio en Dokploy
DB_PORT=5432
DB_WAIT_TIMEOUT=300

# === SSL / HTTPS ===
CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
SECURE_PROXY_SSL_HEADER=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
USE_X_FORWARDED_HOST=True

# === STARTUP ===
RUN_COLLECTSTATIC=True
RUN_MIGRATIONS=True
RUN_SEED=False  # NUNCA True en producción
ADMIN_PASSWORD=tu-contrasena-admin-aqui

# === EMAIL (Opcional) ===
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-contrasena-app-aqui

# === LOGGING (Opcional) ===
SENTRY_DSN=https://tu-sentry-dsn@sentry.io/123456
```

---

## Generar SECRET_KEY Segura

```bash
# Opción 1: Django (si tienes Django instalado localmente)
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Opción 2: Python
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Opción 3: OpenSSL
openssl rand -base64 50
```

Copiar el valor generado a `SECRET_KEY` en Dokploy.

---

## Generar Contraseña Fuerte para PostgreSQL

```bash
# Opción 1: OpenSSL
openssl rand -base64 32

# Opción 2: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Opción 3: Usar gestor de contraseñas
# 1Secure#Pass2025X!
```

---

## Configuración de Dominios en Dokploy

### 1. Agregar Dominio
```
Dashboard → Project: ERP de Kevin → Web Service → Domains
+ Add Domain

Domain Name: tu-dominio.com
Protocol: HTTPS (Auto SSL)
```

### 2. Subdominios (Opcional)
```
+ Add Domain
Domain Name: www.tu-dominio.com
+ Add Domain
Domain Name: api.tu-dominio.com
```

### 3. DNS
Apuntar en tu proveedor de DNS:
```
A Record: tu-dominio.com → IP-DE-TU-SERVIDOR-DOKPLOY
A Record: www.tu-dominio.com → IP-DE-TU-SERVIDOR-DOKPLOY
```

---

## PostgreSQL en Dokploy

### Opción A: Servicio Manage por Dokploy (Recomendado)
1. Dashboard → Project → Services → Add Service
2. Select: Database → PostgreSQL 15
3. Llenar:
   - Database Name: `erp_ventas_prod`
   - Username: `erp_user`
   - Password: `[contraseña generada]`
   - Root Password: `[contraseña generada]`

### Opción B: PostgreSQL Externo (Más Control)
1. Usar servicio PostgreSQL managed (AWS RDS, DigitalOcean, etc.)
2. En Dokploy, solo configurar variables de conexión

---

## Backups de Base de Datos

### Crear Script de Backup Manual

```bash
#!/bin/bash
# File: backup_db.sh

BACKUP_DIR="/mnt/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="erp_ventas_prod"
DB_USER="erp_user"
DB_HOST="localhost"

mkdir -p $BACKUP_DIR

# Hacer dump
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > "$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Comprimir
gzip "$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Eliminar backups > 30 días
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "✓ Backup completed: $BACKUP_DIR/backup_$TIMESTAMP.sql.gz"
```

Ejecutar:
```bash
chmod +x backup_db.sh
./backup_db.sh
```

### Configurar Cron (Automático Diariamente a las 2 AM)

En Dokploy, vía terminal del servidor:
```bash
crontab -e

# Agregar línea:
0 2 * * * /path/to/backup_db.sh >> /var/log/backup_erp.log 2>&1
```

---

## Verificación Pre-Deployment

### Checklist Técnico

- [ ] DNS apunta correctamente
- [ ] SSL se genera automáticamente
- [ ] Migraciones ejecutan sin errores
- [ ] Static files se cargan (admin CSS visible)
- [ ] Media uploads funcionan
- [ ] Admin es accesible
- [ ] Formularios pueden enviarse
- [ ] Sin errores 500

### Test de Connectivity

```bash
# Desde tu terminal local
curl -I https://tu-dominio.com/
# Debe retornar 200-403 (no 502 Bad Gateway)

curl -I https://tu-dominio.com/admin/
# Debe retornar 302 (redirect a login) o 200

curl -I https://tu-dominio.com/static/admin/css/base.css
# Debe retornar 200
```

---

## Troubleshooting Rápido

### Revisar Logs en Tiempo Real
```bash
# Dashboard → Services → [tu-web-service] → Logs
# O terminal del servidor:
docker logs [container-id] --follow
```

### Problema: "502 Bad Gateway"
```bash
# Significa que gunicorn no está respondiendo
# Soluciones:
1. Revisar logs: docker logs [web-container]
2. Revisar migraciones: docker logs [postgres-container]
3. Aumentar DB_WAIT_TIMEOUT a 300 segundos
4. Reiniciar servicio en Dokploy
```

### Problema: "Static files not found"
```bash
# En terminal del servidor:
docker exec [web-container] python manage.py collectstatic --noinput --clear

# Verificar permisos:
docker exec [web-container] ls -la /app/staticfiles/
```

### Problema: "Media files missing"
```bash
# Verificar volumen:
docker volume ls | grep media

# Si no existe, crear:
docker volume create media-persistent

# Revisar montaje en docker-compose
```

---

## Monitoreo Continuo

### Verificaciones Diarias

```bash
# 1. ¿App está respondiendo?
curl https://tu-dominio.com/ -I

# 2. ¿BD está funcionando?
docker exec [postgres-container] pg_isready -U erp_user

# 3. ¿Tamaño de BD?
docker exec [postgres-container] psql -U erp_user -d erp_ventas_prod \
  -c "SELECT pg_size_pretty(pg_database_size('erp_ventas_prod'));"

# 4. ¿Conexiones activas?
docker exec [postgres-container] psql -U erp_user -d erp_ventas_prod \
  -c "SELECT count(*) as active_connections FROM pg_stat_activity;"

# 5. ¿Uso de CPU/RAM?
docker stats [web-container] --no-stream
```

### Alertas Importantes

- **Tamaño BD > 80% del disco**: Hacer limpieza o aumentar espacio
- **Conexiones BD > 90**: Revisar si hay queries lentas
- **Memoria web > 512MB**: App puede estar en memory leak
- **CPU > 80% sostenido**: Considerar horizontal scaling

