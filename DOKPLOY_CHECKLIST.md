# Checklist de Deployment en Dokploy

## ✅ Pre-Deployment

### 1. Seguridad de Django
```bash
# Generar SECRET_KEY segura
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Verificar settings.py
- [ ] `DEBUG = False` en producción
- [ ] `ALLOWED_HOSTS` contiene tu dominio
- [ ] `CSRF_TRUSTED_ORIGINS` contiene tu dominio
- [ ] Certificados SSL configurados
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`

### 3. Base de Datos
- [ ] PostgreSQL versión 15+ (compatible con tu app)
- [ ] Password fuerte para el usuario
- [ ] Backups configurados
- [ ] Verificar conexión desde la app

### 4. Archivos Estáticos y Media
- [ ] `collectstatic` ejecutado
- [ ] Volúmenes persistentes para `/media`
- [ ] Permisos correctos (755 para dirs, 644 para files)

### 5. Pruebas Locales
```bash
# Simular producción localmente
docker-compose -f docker-compose.production.yml up --build

# Verificar que no haya errores
docker logs erp_ventas_web_prod
docker logs erp_ventas_db_prod
```

---

## 🚀 Pasos en Dokploy

### Paso 1: Crear Proyecto
1. Dashboard → Projects → New Project
2. Nombre: `ERP de Kevin`
3. Descripción: `Sistema de gestión de ventas`

### Paso 2: Agregar Servicio (Web)
1. **Repository Configuration**
   - Git URL: Tu repositorio
   - Branch: `main` (o la que uses)
   - Dockerfile Path: `./Dockerfile`

2. **Build Configuration**
   - Build Context: `.`
   - Build Method: `Dockerfile`

3. **Environment Variables**
```
SECRET_KEY=<generar-nueva>
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=erp_ventas_prod
DB_USER=erp_user
DB_PASSWORD=<contraseña-fuerte>
DB_HOST=postgres-service
DB_PORT=5432
CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
SECURE_PROXY_SSL_HEADER=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
RUN_COLLECTSTATIC=True
RUN_MIGRATIONS=True
RUN_SEED=False
ADMIN_PASSWORD=<contraseña-fuerte>
```

4. **Ports**
   - Internal Port: `8000`
   - Expose: Sí
   - Port: `80` → `8000` (http)

5. **Volumes**
   - `/app/media` → `media-persistent`
   - `/app/staticfiles` → `static-persistent`

### Paso 3: Agregar PostgreSQL
1. **Add Service** → Database → PostgreSQL 15
2. **Credentials**
   - Username: `erp_user`
   - Password: <contraseña-fuerte>
   - Database: `erp_ventas_prod`

3. **Port Mapping**
   - Internal: `5432`
   - External: `5432` (opcional, para backups)

4. **Volumes**
   - `/var/lib/postgresql/data` → `postgres-data-prod`

5. **Health Check** (ya debe estar)
   - Command: `pg_isready -U erp_user -d erp_ventas_prod`

### Paso 4: Conectar Servicios
1. En la configuración de la app web:
   - `DB_HOST` debe apuntar al nombre del servicio PostgreSQL en Dokploy
   - Depende de cómo Dokploy nombre los servicios (ej: `postgres`, `db`, o `postgres-service`)

### Paso 5: SSL/HTTPS
1. Dokploy → Domain Settings
2. Add Domain: `tu-dominio.com`
3. Enable SSL (automático con Let's Encrypt)
4. Redirect HTTP → HTTPS

### Paso 6: Backup Automático
```bash
# En Dokploy, configurar cron job para backups
# Ejecutar diariamente a las 2 AM
0 2 * * * pg_dump -U erp_user -d erp_ventas_prod > /backups/$(date +\%Y\%m\%d_\%H\%M\%S).sql
```

---

## 🔍 Errores Comunes y Soluciones

### Error 1: "Database is unavailable at startup"
```
✗ psycopg2.OperationalError: could not connect to server
```
**Causa**: PostgreSQL no está listo cuando Django inicia

**Solución**:
- Aumentar `DB_WAIT_TIMEOUT` a 300 (5 minutos)
- Verificar que los servicios estén en la misma red
- Revisar logs: `docker logs [postgres-container]`

---

### Error 2: "Static files not found (404)"
```
GET /static/admin/css/base.css HTTP/1.1" 404
```
**Causa**: `collectstatic` no se ejecutó o falló

**Solución**:
- Asegurar `RUN_COLLECTSTATIC=True`
- Revisar permisos de `/app/staticfiles`
- En Dokploy, crear volumen persistente para staticfiles
- Comando manual:
  ```bash
  docker exec [web-container] python manage.py collectstatic --noinput --clear
  ```

---

### Error 3: "Media files disappearing after restart"
```
GET /media/documents/invoice.pdf HTTP/1.1" 404
```
**Causa**: `/app/media` no tiene volumen persistente

**Solución**:
- En Dokploy, agregar volumen: `/app/media` → `media-persistent`
- Dar permisos: `chmod 755 /app/media`

---

### Error 4: "Migration conflicts"
```
django.db.migrations.exceptions.ConflictError: Conflicting migrations
```
**Causa**: Múltiples migraciones en desarrollo, luego integradas en producción

**Solución**:
- Hacer merge de migraciones en desarrollo:
  ```bash
  python manage.py makemigrations --merge
  ```
- Probar migraciones localmente antes de deployar:
  ```bash
  docker-compose -f docker-compose.production.yml up
  docker-compose -f docker-compose.production.yml down -v
  ```

---

### Error 5: "CSRF token missing or incorrect"
```
Forbidden (403): /form-submit/
CSRF verification failed.
```
**Causa**: `CSRF_TRUSTED_ORIGINS` no incluye tu dominio

**Solución**:
```bash
CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
SECURE_PROXY_SSL_HEADER=True  # Si está detrás de proxy
```

---

### Error 6: "Debug information leaking in production"
```
Unsafe redirect (403)
```
**Causa**: `DEBUG=True` con `SECURE_SSL_REDIRECT=True`

**Solución**:
```bash
DEBUG=False
SECURE_SSL_REDIRECT=True
```

---

## 📊 Monitoreo en Dokploy

### Ver Logs
```bash
# Desde dashboard
Dokploy → Project → Services → [tu-app] → Logs

# O manualmente
docker logs [container-id] --follow
```

### Verificar Salud
```bash
# Acceder a la app
curl https://tu-dominio.com/

# Ver admin
curl https://tu-dominio.com/admin/

# Ver base de datos
docker exec [postgres-container] psql -U erp_user -d erp_ventas_prod -c "SELECT version();"
```

### Monitorar Performance
```bash
# Recursos
docker stats [web-container]

# Conexiones a BD
docker exec [postgres-container] psql -U erp_user -d erp_ventas_prod -c "SELECT count(*) FROM pg_stat_activity;"

# Tamaño BD
docker exec [postgres-container] psql -U erp_user -d erp_ventas_prod -c "SELECT pg_size_pretty(pg_database_size('erp_ventas_prod'));"
```

---

## 🛡️ Hardening Adicional

### 1. Desactivar Panel Admin en Producción (Opcional pero Recomendado)
```python
# config/urls.py
if not settings.DEBUG:
    urlpatterns = [url for url in urlpatterns if '/admin/' not in str(url)]
```

### 2. Rate Limiting
```bash
# Agregar a requirements.txt
django-ratelimit==4.1.0

# Usar en vistas críticas
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h')
def login_view(request):
    ...
```

### 3. Web Application Firewall
- Usar Cloudflare gratuito delante de tu app
- Habilitar protección contra ataques comunes

### 4. Backup Diferencial
```bash
# Script para backup automático
#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +\%Y\%m\%d_\%H\%M\%S)

pg_dump -U erp_user -d erp_ventas_prod > "$BACKUP_DIR/full_$TIMESTAMP.sql"
gzip "$BACKUP_DIR/full_$TIMESTAMP.sql"

# Eliminar backups mayores a 30 días
find $BACKUP_DIR -name "full_*.sql.gz" -mtime +30 -delete
```

---

## 📋 Checklist Final Pre-Go Live

- [ ] Secret key es verdaderamente secreto (no en git)
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS incluye dominio real
- [ ] CSRF_TRUSTED_ORIGINS configurado
- [ ] SSL/HTTPS funciona
- [ ] Migraciones ejecutadas
- [ ] collectstatic ejecutado
- [ ] Volúmenes persistentes para media
- [ ] Backups automáticos configurados
- [ ] Logs monitoreados
- [ ] Admin password cambiado
- [ ] Correo funciona (test email)
- [ ] Formularios funcionan (test CSRF)
- [ ] Descargas de archivos funcionan
- [ ] Carga de imágenes funciona
- [ ] Performance aceptable (< 2s por página)
- [ ] Errores 500 loguean correctamente
- [ ] No hay secrets en variables públicas

