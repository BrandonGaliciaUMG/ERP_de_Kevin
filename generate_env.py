#!/usr/bin/env python3
"""
Generador de variables de entorno seguras para Dokploy
Uso: python generate_env.py
"""

import secrets
import string
from pathlib import Path
from datetime import datetime

def generate_secret_key(length=50):
    """Generar SECRET_KEY segura para Django"""
    return secrets.token_urlsafe(length)

def generate_password(length=32, special_chars=True):
    """Generar contraseña fuerte"""
    if special_chars:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    else:
        alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_env_file(output_file=".env.production"):
    """Generar archivo .env.production con valores seguros"""
    
    secret_key = generate_secret_key()
    db_password = generate_password(32, special_chars=False)  # Sin chars especiales para evitar escape issues
    admin_password = generate_password(16)
    
    env_content = f"""# ============================================================================
# ERP de Kevin - Configuración de Producción (Dokploy)
# Generado: {datetime.now().isoformat()}
# ============================================================================
# ⚠️ IMPORTANTE: NO SUBIR ESTE ARCHIVO A GIT
# Agregar a .gitignore: .env.production
# ============================================================================

# === SEGURIDAD ===
SECRET_KEY={secret_key}
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# === BASE DE DATOS ===
DB_ENGINE=django.db.backends.postgresql
DB_NAME=erp_ventas_prod
DB_USER=erp_user
DB_PASSWORD={db_password}
DB_HOST=postgres-service
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
RUN_SEED=False
ADMIN_PASSWORD={admin_password}

# === EMAIL (Opcional) ===
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=tu-email@gmail.com
# EMAIL_HOST_PASSWORD=tu-contrasena-app

# === LOGGING (Opcional) ===
# SENTRY_DSN=https://tu-sentry-dsn@sentry.io/123456

# ============================================================================
# PRÓXIMOS PASOS:
# 1. Reemplazar 'tu-dominio.com' con tu dominio real
# 2. Cambiar contraseñas si lo deseas (copiar valores de arriba)
# 3. Agregar en Dokploy → Project → Web Service → Environment Variables
# 4. NO subir a git
# ============================================================================
"""
    
    # Escribir archivo
    with open(output_file, 'w') as f:
        f.write(env_content)
    
    print(f"✓ Archivo creado: {output_file}")
    print("\n" + "="*70)
    print("VALORES GENERADOS (Guardar en lugar seguro)")
    print("="*70)
    print(f"\nSECRET_KEY:\n{secret_key}")
    print(f"\nDB_PASSWORD:\n{db_password}")
    print(f"\nADMIN_PASSWORD:\n{admin_password}")
    print("\n" + "="*70)
    print("\nPróximos pasos:")
    print("1. Editar .env.production y reemplazar 'tu-dominio.com' con tu dominio")
    print("2. Copiar el contenido a Dokploy → Web Service → Environment Variables")
    print("3. Guardar contraseñas en gestor de contraseñas (1Password, LastPass, etc)")
    print("4. Eliminar este archivo después de usar: rm .env.production")
    print("="*70)

if __name__ == "__main__":
    generate_env_file()
