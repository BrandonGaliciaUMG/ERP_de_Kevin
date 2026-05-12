# Variables de Entorno Completas para Dokploy

## 📋 Tabla de Contenidos
1. [Variables Obligatorias](#variables-obligatorias)
2. [Variables de Seguridad](#variables-de-seguridad)
3. [Variables de Base de Datos](#variables-de-base-de-datos)
4. [Variables de SSL/HTTPS](#variables-de-sslhttps)
5. [Variables de Startup](#variables-de-startup)
6. [Variables Opcionales](#variables-opcionales)
7. [Valores Ejemplo Completo](#valores-ejemplo-completo)

---

## Variables Obligatorias

Estas DEBEN estar configuradas para que la app funcione:

### SECRET_KEY
```
SECRET_KEY=django-insecure-8x@5=n_2rvq8!@t#2x$%^&*(z9k_l+p0q=r@!$%^&*()_+-
```
- **Descripción**: Clave secreta para firmar cookies y tokens
- **Generarlo con**: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- **Importante**: NO usar valores por defecto
- **Cambio**: Si se filtra, cambiar y redeploy (invalidará todas las sesiones)

### DEBUG
```
DEBUG=False
```
- **Descripción**: Desactivar modo debug en producción
- **Valores**: `True` o `False`
- **Nunca**: `True` en producción (expone información sensible)
- **Recomendado**: `False` siempre

### ALLOWED_HOSTS
```
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
```
- **Descripción**: Dominios que Django acepta
- **Formato**: Separados por comas, SIN espacios
- **Ejemplos**:
  - `erp.miempresa.com`
  - `erp.miempresa.com,www.erp.miempresa.com`
  - `192.168.1.100` (para IP local)
- **Importante**: Debe incluir el dominio de Dokploy

---

## Variables de Seguridad

Configuración de seguridad de Django:

```
# === SEGURIDAD BÁSICA ===
SECRET_KEY=tu-clave-secreta-generada
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# === COOKIES Y SESIONES ===
SESSION_COOKIE_SECURE=True              # Solo enviar por HTTPS
CSRF_COOKIE_SECURE=True                 # Solo enviar por HTTPS
SECURE_SSL_REDIRECT=True                # Redirigir HTTP a HTTPS

# === HSTS (HTTP Strict Transport Security) ===
SECURE_HSTS_SECONDS=31536000           # 1 año en segundos
SECURE_HSTS_INCLUDE_SUBDOMAINS=True    # Aplicar a subdomios
SECURE_HSTS_PRELOAD=True               # Incluir en HSTS preload list

# === PROXY Y HEADERS ===
SECURE_PROXY_SSL_HEADER=True           # Si está detrás de proxy (Dokploy)
USE_X_FORWARDED_HOST=True              # Confiar en headers de proxy

# === CSRF ===
CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
```

| Variable | Valor | Explicación |
|----------|-------|-------------|
| `SESSION_COOKIE_SECURE` | `True` | Las cookies de sesión solo se envían por HTTPS |
| `CSRF_COOKIE_SECURE` | `True` | Token CSRF solo por HTTPS |
| `SECURE_SSL_REDIRECT` | `True` | Redirigir automáticamente HTTP → HTTPS |
| `SECURE_HSTS_SECONDS` | `31536000` | 1 año (31536000 segundos) |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `True` | HSTS aplica a subdominios |
| `SECURE_HSTS_PRELOAD` | `True` | Preload en navegadores |
| `SECURE_PROXY_SSL_HEADER` | `True` | Confiar en proxy (Dokploy) |
| `USE_X_FORWARDED_HOST` | `True` | Usar host del header forwarded |
| `CSRF_TRUSTED_ORIGINS` | URLs HTTPS | Origen de formularios permitidos |

---

## Variables de Base de Datos

Configuración de conexión a PostgreSQL:

```
# === MOTOR DE BD ===
DB_ENGINE=django.db.backends.postgresql

# === CREDENCIALES ===
DB_NAME=erp_ventas_prod
DB_USER=erp_user
DB_PASSWORD=contraseña-fuerte-aqui
DB_HOST=db  # Nombre del servicio en Dokploy
DB_PORT=5432

# === TIMEOUTS ===
DB_WAIT_TIMEOUT=300
```

| Variable | Valor | Explicación |
|----------|-------|-------------|
| `DB_ENGINE` | `django.db.backends.postgresql` | Motor de BD (NO cambiar) |
| `DB_NAME` | `erp_ventas_prod` | Nombre de la BD PostgreSQL |
| `DB_USER` | `erp_user` | Usuario de PostgreSQL |
| `DB_PASSWORD` | Contraseña fuerte | Generada con: `openssl rand -base64 32` |
| `DB_HOST` | `db` o `postgres-service` | Nombre del servicio (ver en Dokploy) |
| `DB_PORT` | `5432` | Puerto de PostgreSQL (no cambiar) |
| `DB_WAIT_TIMEOUT` | `300` | Segundos a esperar (5 minutos) |

**Importante**: `DB_HOST` depende de cómo Dokploy nombre los servicios. Valores comunes:
- `db`
- `postgres`
- `postgres-service`
- Verificar en los logs al deployar

---

## Variables de SSL/HTTPS

Para certificados y HTTPS:

```
# === SSL ===
CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
SECURE_PROXY_SSL_HEADER=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

**Nota**: Dokploy auto-genera certificados Let's Encrypt. No necesitas configurar claves aquí.

---

## Variables de Startup

Controlan qué se ejecuta al iniciar:

```
# === STARTUP TASKS ===
RUN_COLLECTSTATIC=True      # Recolectar archivos estáticos (CSS, JS)
RUN_MIGRATIONS=True         # Ejecutar migraciones de BD
RUN_SEED=False              # NUNCA True en producción
ADMIN_PASSWORD=contraseña   # Contraseña del usuario admin
```

| Variable | Valor | Explicación |
|----------|-------|-------------|
| `RUN_COLLECTSTATIC` | `True` | Ejecutar `collectstatic` (necesario) |
| `RUN_MIGRATIONS` | `True` | Ejecutar migraciones de BD |
| `RUN_SEED` | `False` | Insertar datos de prueba (NUNCA en prod) |
| `ADMIN_PASSWORD` | Contraseña | Password para usuario `admin` |

---

## Variables Opcionales

Útiles pero no obligatorias:

### Email (SMTP)
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-aqui
```

**Generar App Password en Gmail**:
1. Ir a myaccount.google.com
2. Security → App passwords
3. Copiar la contraseña generada (16 caracteres)

### Sentry (Error Tracking)
```
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/123456
```

### Timezone
```
TZ=America/Bogota
```

### Logging (Opcional)
```
LOG_LEVEL=INFO
```

---

## Valores Ejemplo Completo

### Versión Minimalista (Lo Mínimo)

```
SECRET_KEY=django-insecure-4z@9m_3rvq8!@t#2x$%^&*(z9k_l+p0q=r@!$%^&*()_+-
DEBUG=False
ALLOWED_HOSTS=erp.witzbe.tech,www.erp.witzbe.tech
DB_ENGINE=django.db.backends.postgresql
DB_NAME=erp_ventas_prod
DB_USER=erp_user
DB_PASSWORD=PruebaErp2024!Witzbe123
DB_HOST=db
DB_PORT=5432
DB_WAIT_TIMEOUT=300
CSRF_TRUSTED_ORIGINS=https://erp.witzbe.tech,https://www.erp.witzbe.tech
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
RUN_COLLECTSTATIC=True
RUN_MIGRATIONS=True
RUN_SEED=False
ADMIN_PASSWORD=AdminTest2024!Erp
```

### Versión Completa (Recomendada)

```
# ============================================================================
# SEGURIDAD
# ============================================================================
SECRET_KEY=django-insecure-4z@9m_3rvq8!@t#2x$%^&*(z9k_l+p0q=r@!$%^&*()_+-
DEBUG=False
ALLOWED_HOSTS=erp.witzbe.tech,www.erp.witzbe.tech

# ============================================================================
# BASE DE DATOS
# ============================================================================
DB_ENGINE=django.db.backends.postgresql
DB_NAME=erp_ventas_prod
DB_USER=erp_user
DB_PASSWORD=PruebaErp2024!Witzbe123
DB_HOST=db
DB_PORT=5432
DB_WAIT_TIMEOUT=300

# ============================================================================
# SSL / HTTPS / SEGURIDAD ADICIONAL
# ============================================================================
CSRF_TRUSTED_ORIGINS=https://erp.witzbe.tech,https://www.erp.witzbe.tech
SECURE_PROXY_SSL_HEADER=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
USE_X_FORWARDED_HOST=True

# ============================================================================
# STARTUP
# ============================================================================
RUN_COLLECTSTATIC=True
RUN_MIGRATIONS=True
RUN_SEED=False
ADMIN_PASSWORD=AdminTest2024!Erp

# ============================================================================
# EMAIL (Opcional pero recomendado)
# ============================================================================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-gmail

# ============================================================================
# TIMEZONE
# ============================================================================
TZ=America/Bogota

# ============================================================================
# SENTRY (Opcional para monitoreo de errores)
# ============================================================================
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/123456
```

---

## 🔑 Generar Valores Seguros

### Generar SECRET_KEY

```bash
# Opción 1: Django
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Opción 2: Python
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Opción 3: OpenSSL
openssl rand -base64 50

# Opción 4: Usar script incluido
python generate_env.py
```

### Generar Contraseña para DB_PASSWORD

```bash
# Opción 1: OpenSSL
openssl rand -base64 32

# Opción 2: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Opción 3: Generar múltiples
for i in {1..3}; do openssl rand -base64 32; done
```

### Generar ADMIN_PASSWORD

```bash
# Opción 1: OpenSSL
openssl rand -base64 16

# Opción 2: Python
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

---

## ✅ Checklist de Validación

Antes de deployar en Dokploy, verificar:

- [ ] `SECRET_KEY` es una cadena aleatoria (no valor por defecto)
- [ ] `DEBUG=False` (NUNCA `True` en producción)
- [ ] `ALLOWED_HOSTS` incluye tu dominio real
- [ ] `DB_PASSWORD` es fuerte (+ de 32 caracteres)
- [ ] `DB_HOST` es el nombre correcto del servicio PostgreSQL en Dokploy
- [ ] `CSRF_TRUSTED_ORIGINS` incluye tu dominio con HTTPS
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `CSRF_COOKIE_SECURE=True`
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] `RUN_MIGRATIONS=True`
- [ ] `RUN_SEED=False` (NUNCA en producción)
- [ ] `ADMIN_PASSWORD` es fuerte
- [ ] Todas las variables están en Dokploy (no en git)
- [ ] `.env.production` está en `.gitignore`

---

## 📝 Pasos para Agregar en Dokploy

### 1. En Dashboard
```
Dokploy → Project: ERP de Kevin → Web Service → Environment Variables
```

### 2. Click en "+ Add"
Copiar cada variable:
```
KEY=VALUE
```

### 3. Agregar todas las variables

### 4. Click en "Save" o "Deploy"

### 5. Verificar en Logs
```
Dokploy → Services → Logs
```

---

## 🚨 Errores Comunes por Variables

| Error | Causa | Solución |
|-------|-------|----------|
| `DisallowedHost` | `ALLOWED_HOSTS` incorrecto | Incluir tu dominio |
| `ImproperlyConfigured` | `SECRET_KEY` falta | Generar con comando |
| `OperationalError: could not connect` | `DB_HOST` incorrecto | Verificar nombre del servicio |
| `CSRF verification failed` | `CSRF_TRUSTED_ORIGINS` incorrecto | Debe ser HTTPS |
| `Static files 404` | `RUN_COLLECTSTATIC=False` | Cambiar a `True` |
| `Migration failed` | `DB_PASSWORD` incorrecto | Verificar caracteres especiales |

