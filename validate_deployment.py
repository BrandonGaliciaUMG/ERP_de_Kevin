#!/usr/bin/env python3
"""
Script de validación pre-deployment para Dokploy
Verifica que el proyecto esté listo para producción
Uso: python validate_deployment.py
"""

import os
import sys
import json
from pathlib import Path
from django.core.management import call_command

# ANSI Colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

def check(condition, message, required=True):
    """Verificar una condición y mostrar resultado"""
    if condition:
        print(f"{GREEN}✓{NC} {message}")
        return True
    else:
        status = f"{RED}✗ CRITICAL{NC}" if required else f"{YELLOW}⚠ WARNING{NC}"
        print(f"{status}: {message}")
        return condition

def check_file_exists(path, description):
    """Verificar que un archivo existe"""
    exists = Path(path).exists()
    status = "found" if exists else "missing"
    return check(exists, f"{description} ({status})", required=not exists)

def check_env_variable(var_name, required=True):
    """Verificar variable de entorno"""
    value = os.getenv(var_name)
    if value:
        print(f"{GREEN}✓{NC} {var_name} = {value[:20]}..." if len(value) > 20 else f"{GREEN}✓{NC} {var_name} = {value}")
        return True
    else:
        status = f"{RED}✗{NC}" if required else f"{YELLOW}⚠{NC}"
        print(f"{status} {var_name}: not set" + (" (REQUIRED)" if required else " (optional)"))
        return not required

def main():
    print(f"\n{BLUE}{'='*70}{NC}")
    print(f"{BLUE}ERP de Kevin - Pre-Deployment Validation for Dokploy{NC}")
    print(f"{BLUE}{'='*70}{NC}\n")
    
    critical_failures = []
    warnings = []
    
    # =========================================================================
    # 1. Verificar Archivos Críticos
    # =========================================================================
    print(f"{BLUE}1. Checking Critical Files{NC}")
    print("-" * 70)
    
    required_files = [
        ("config/settings.py", "Django settings"),
        ("config/wsgi.py", "WSGI application"),
        ("manage.py", "Django management"),
        ("Dockerfile", "Docker image definition"),
        ("requirements.txt", "Python dependencies"),
        ("docker/entrypoint.sh", "Entrypoint script"),
    ]
    
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            critical_failures.append(f"Missing file: {file_path}")
    
    # =========================================================================
    # 2. Verificar Dependencias de Python
    # =========================================================================
    print(f"\n{BLUE}2. Checking Python Dependencies{NC}")
    print("-" * 70)
    
    required_packages = {
        'django': 'Django',
        'psycopg': 'PostgreSQL adapter',
        'gunicorn': 'Production server',
        'whitenoise': 'Static files',
    }
    
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"{GREEN}✓{NC} {description} ({package})")
        except ImportError:
            critical_failures.append(f"Missing package: {package}")
            print(f"{RED}✗ CRITICAL{NC}: {description} ({package}) - not installed")
    
    # =========================================================================
    # 3. Verificar Configuración de Django
    # =========================================================================
    print(f"\n{BLUE}3. Checking Django Configuration{NC}")
    print("-" * 70)
    
    from django.conf import settings
    
    checks = {
        'DEBUG is False': (not settings.DEBUG, "DEBUG should be False in production"),
        'SECRET_KEY is set': (settings.SECRET_KEY and 'change-this' not in settings.SECRET_KEY, "SECRET_KEY should be secure"),
        'ALLOWED_HOSTS configured': (len(settings.ALLOWED_HOSTS) > 0, "ALLOWED_HOSTS should include your domain"),
        'Database configured': (settings.DATABASES.get('default', {}).get('ENGINE'), "Database engine should be PostgreSQL"),
        'Static files root set': (hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT, "STATIC_ROOT should be configured"),
        'Media root set': (hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT, "MEDIA_ROOT should be configured"),
        'WhiteNoise configured': ('whitenoise' in [m for m in settings.MIDDLEWARE if 'whitenoise' in m.lower()], "WhiteNoise should be in MIDDLEWARE"),
    }
    
    for check_name, (condition, message) in checks.items():
        if not condition:
            critical_failures.append(message)
            print(f"{RED}✗ CRITICAL{NC}: {message}")
        else:
            print(f"{GREEN}✓{NC} {message}")
    
    # =========================================================================
    # 4. Verificar Variable de Entorno para Producción
    # =========================================================================
    print(f"\n{BLUE}4. Checking Environment Variables for Production{NC}")
    print("-" * 70)
    
    prod_vars = {
        'SECRET_KEY': True,
        'DEBUG': True,
        'ALLOWED_HOSTS': False,
        'DB_ENGINE': True,
        'DB_NAME': True,
        'DB_USER': True,
        'DB_PASSWORD': True,
        'DB_HOST': False,
        'CSRF_TRUSTED_ORIGINS': False,
        'SECURE_SSL_REDIRECT': False,
        'SESSION_COOKIE_SECURE': False,
    }
    
    for var, required in prod_vars.items():
        if not check_env_variable(var, required=required):
            if required:
                critical_failures.append(f"Missing required env var: {var}")
            else:
                warnings.append(f"Missing optional env var: {var}")
    
    # =========================================================================
    # 5. Verificar Migraciones
    # =========================================================================
    print(f"\n{BLUE}5. Checking Migrations{NC}")
    print("-" * 70)
    
    try:
        # Verificar que no haya migraciones pendientes
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        call_command('showmigrations', plan=True, stdout=out)
        output = out.getvalue()
        
        if '[X]' in output and '[ ]' not in output:
            print(f"{GREEN}✓{NC} All migrations are applied")
        else:
            print(f"{YELLOW}⚠{NC} Some migrations may be pending (verify manually)")
    except Exception as e:
        warnings.append(f"Could not check migrations: {e}")
        print(f"{YELLOW}⚠{NC} Could not check migrations: {e}")
    
    # =========================================================================
    # 6. Verificar Existencia de .env.production
    # =========================================================================
    print(f"\n{BLUE}6. Checking Production Environment File{NC}")
    print("-" * 70)
    
    if Path(".env.production").exists():
        print(f"{GREEN}✓{NC} .env.production file exists")
        print(f"{YELLOW}⚠{NC} Make sure it's NOT committed to git")
        # Verificar .gitignore
        gitignore_path = Path(".gitignore")
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                if '.env.production' in f.read():
                    print(f"{GREEN}✓{NC} .env.production is in .gitignore")
                else:
                    warnings.append("Add .env.production to .gitignore")
                    print(f"{YELLOW}⚠{NC} Add .env.production to .gitignore")
    else:
        print(f"{YELLOW}⚠{NC} .env.production not found (run: python generate_env.py)")
    
    # =========================================================================
    # 7. Verificar Docker Configuration
    # =========================================================================
    print(f"\n{BLUE}7. Checking Docker Configuration{NC}")
    print("-" * 70)
    
    if Path("docker-compose.production.yml").exists():
        print(f"{GREEN}✓{NC} docker-compose.production.yml exists")
    else:
        warnings.append("docker-compose.production.yml not found")
        print(f"{YELLOW}⚠{NC} docker-compose.production.yml not found")
    
    # =========================================================================
    # Resumen Final
    # =========================================================================
    print(f"\n{BLUE}{'='*70}{NC}")
    print(f"{BLUE}VALIDATION SUMMARY{NC}")
    print(f"{BLUE}{'='*70}{NC}\n")
    
    if critical_failures:
        print(f"{RED}CRITICAL FAILURES ({len(critical_failures)}){NC}")
        for i, failure in enumerate(critical_failures, 1):
            print(f"  {i}. {failure}")
    
    if warnings:
        print(f"\n{YELLOW}WARNINGS ({len(warnings)}){NC}")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
    
    if not critical_failures and not warnings:
        print(f"{GREEN}✓ ALL CHECKS PASSED!{NC}")
        print(f"\nYour application is ready for Dokploy deployment.")
    elif not critical_failures:
        print(f"\n{YELLOW}✓ Ready for deployment (with warnings - review above){NC}")
    else:
        print(f"\n{RED}✗ NOT READY for deployment{NC}")
        print(f"Please fix the critical failures above before deploying.")
    
    # Recomendaciones finales
    print(f"\n{BLUE}{'='*70}{NC}")
    print(f"{BLUE}NEXT STEPS{NC}")
    print(f"{BLUE}{'='*70}{NC}\n")
    
    print("1. Local Testing (Simulate Production):")
    print("   docker-compose -f docker-compose.production.yml up --build")
    print()
    print("2. Verify Everything Works:")
    print("   - http://localhost/admin/ (login with admin/[password])")
    print("   - http://localhost/static/admin/css/base.css (static files)")
    print("   - Upload a file to /media/ (media persistence)")
    print()
    print("3. Generate Secure Environment Variables:")
    print("   python generate_env.py")
    print()
    print("4. Deploy to Dokploy:")
    print("   - Create project in Dokploy dashboard")
    print("   - Add environment variables from .env.production")
    print("   - Configure domain and SSL")
    print("   - Deploy")
    print()
    print("5. Monitor Deployment:")
    print("   - Check logs: Dokploy → Services → Logs")
    print("   - Verify health: curl https://your-domain.com/")
    print()
    
    print(f"{BLUE}{'='*70}{NC}\n")
    
    # Return exit code
    return 1 if critical_failures else 0

if __name__ == "__main__":
    sys.exit(main())
