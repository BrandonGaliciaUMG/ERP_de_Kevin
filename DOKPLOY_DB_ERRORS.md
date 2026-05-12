# Evitar Errores de Base de Datos en Dokploy

## 🎯 Errores Comunes y Soluciones

### 1. "Database is unavailable at startup"

#### Síntoma
```
psycopg2.OperationalError: could not connect to server: Connection refused
```

#### Causas
- PostgreSQL tarda más de lo esperado en iniciar
- Networking incorrecto entre contenedores
- Volumen de datos corrupto

#### Soluciones

**A. Aumentar timeout de espera**
```yaml
# En Dokploy, variable de entorno:
DB_WAIT_TIMEOUT=300  # 5 minutos en lugar de 180 segundos

# En docker-compose.production.yml:
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
  interval: 10s
  timeout: 5s
  retries: 10  # Aumentar de 5 a 10
  start_period: 30s  # Agregar espacio de "calentamiento"
```

**B. Verifying network connectivity**
```bash
# En terminal del servidor Dokploy:
docker network ls
docker network inspect [network-name]

# Ambos contenedores deben estar en la misma red
docker network connect [network] [web-container]
```

**C. Reparar volumen de datos**
```bash
# Si el volumen está corrupto:
docker volume rm postgres-data-prod
# Advertencia: ESTO BORRA TODOS LOS DATOS

# Mejor: Hacer backup primero
docker run --rm -v postgres-data-prod:/data -v $(pwd):/backup \
  postgres:15-alpine pg_dump -U erp_user -d erp_ventas_prod > backup.sql
```

---

### 2. "Migrations Conflict"

#### Síntoma
```
django.db.migrations.exceptions.ConflictError: Conflicting migrations detected
```

#### Causa
Dos o más ramas con migraciones del mismo número (0002_auto.py en dos lugares)

#### Soluciones

**A. Resolver localmente antes de deployar**
```bash
# En desarrollo:
python manage.py makemigrations --merge
git add apps/*/migrations/
git commit -m "Merge migrations"
git push
```

**B. Si ya está en producción**
```bash
# Backup primero
docker exec [postgres-container] pg_dump -U erp_user -d erp_ventas_prod > backup.sql

# Entrar al contenedor
docker exec -it [web-container] bash

# Marcar migraciones como falsas (si no son críticas)
python manage.py migrate --fake [app] [migration-name]

# Resolver conflictos manualmente
python manage.py makemigrations --merge
python manage.py migrate
```

---

### 3. "Migration Applied Twice"

#### Síntoma
```
django.db.IntegrityError: duplicate key value violates unique constraint
```

#### Causa
Una migración se ejecutó dos veces (entrypoint.sh corre dos veces)

#### Soluciones

**A. Revisión de entrypoint.sh**
```bash
# Verificar que migrate se ejecute UNA SOLA VEZ
# En entrypoint.sh:
if is_true "${RUN_MIGRATIONS:-True}"; then
    python manage.py migrate --noinput
    # No debe haber un segundo migrate acá
fi
```

**B. Configurar RUN_MIGRATIONS en Dokploy**
```bash
# Variables de entorno en Dokploy:
RUN_MIGRATIONS=True   # Primera vez
RUN_MIGRATIONS=False  # Deployments posteriores (manual)
```

---

### 4. "Foreign Key Constraint Violation"

#### Síntoma
```
psycopg2.errors.ForeignKeyViolation: insert or update on table "pedidos_pedido" 
violates foreign key constraint "pedidos_pedido_cliente_id_fkey"
```

#### Causa
- Migraciones de FK ejecutadas en orden incorrecto
- Datos inconsistentes en BD

#### Soluciones

**A. Ajustar orden de migraciones**
```python
# En migration que crea FK:
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('clientes', '0001_initial'),  # DEBE existir antes
        ('pedidos', '0001_initial'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='pedido',
            name='cliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clientes.cliente'),
        ),
    ]
```

**B. Limpiar datos inconsistentes**
```python
# En shell de Django:
python manage.py shell

from apps.pedidos.models import Pedido
from apps.clientes.models import Cliente

# Encontrar pedidos sin cliente válido
orphaned = Pedido.objects.filter(cliente_id__isnull=True)
print(f"Orphaned pedidos: {orphaned.count()}")

# Opción 1: Eliminar
orphaned.delete()

# Opción 2: Asignar a cliente por defecto
default_cliente = Cliente.objects.first()
orphaned.update(cliente=default_cliente)
```

---

### 5. "Transaction Aborted Errors"

#### Síntoma
```
InternalError: current transaction is aborted
CommandError: Transaction aborted. Discarding command.
```

#### Causa
Migración falló a mitad de camino, dejando la transacción en estado inconsistente

#### Soluciones

**A. Reset de transacción**
```bash
# En terminal del servidor:
docker exec [postgres-container] psql -U erp_user -d erp_ventas_prod
# En psql:
ROLLBACK;
SELECT * FROM django_migrations ORDER BY id DESC LIMIT 5;
```

**B. Deshacer último conjunto de migraciones**
```bash
# En Django shell:
python manage.py migrate [app] [previous-migration]

# Ej:
python manage.py migrate pedidos 0001_initial
```

**C. Aplicar nuevamente**
```bash
python manage.py migrate
```

---

### 6. "Database Does Not Exist"

#### Síntoma
```
FATAL: database "erp_ventas_prod" does not exist
```

#### Causa
PostgreSQL se reinició o se eliminó el contenedor sin volumen persistente

#### Soluciones

**Verificar volumen**
```bash
docker volume ls | grep postgres

# Si no existe:
docker volume create postgres-data-prod

# En Dokploy, re-crear el servicio apuntando a este volumen
```

**Crear BD manualmente**
```bash
docker exec [postgres-container] psql -U postgres
# En psql:
CREATE DATABASE erp_ventas_prod OWNER erp_user;
```

**Restaurar desde backup**
```bash
docker exec -i [postgres-container] psql -U erp_user -d erp_ventas_prod < backup.sql
```

---

### 7. "Disk Space Issues"

#### Síntoma
```
ERROR: could not write block 12345: No space left on device
```

#### Causa
PostgreSQL creció demasiado o logs sin rotar

#### Soluciones

**A. Ver uso de disco**
```bash
# En servidor:
df -h

# Tamaño de BD:
docker exec [postgres-container] psql -U erp_user -d erp_ventas_prod \
  -c "SELECT pg_size_pretty(pg_database_size('erp_ventas_prod'));"

# Tablas grandes:
docker exec [postgres-container] psql -U erp_user -d erp_ventas_prod \
  -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) \
       FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;"
```

**B. Limpiar datos innecesarios**
```python
# En Django shell:
from apps.pedidos.models import Pedido
from django.utils import timezone
from datetime import timedelta

# Eliminar pedidos antiguos (> 1 año)
old_date = timezone.now() - timedelta(days=365)
deleted = Pedido.objects.filter(fecha_pedido__lt=old_date).delete()
print(f"Deleted {deleted[0]} old pedidos")

# VACUUM para recuperar espacio
python manage.py shell -c "from django.db import connection; connection.cursor().execute('VACUUM ANALYZE')"
```

**C. Agregar espacio**
```bash
# En Dokploy, aumentar tamaño del volumen (dependiendo del proveedor)
# DigitalOcean: Resize Volume
# AWS: Extend EBS Volume
# etc.
```

---

### 8. "Max Connections Exceeded"

#### Síntoma
```
FATAL: too many connections for role "erp_user"
```

#### Causa
Django/gunicorn abriendo demasiadas conexiones simultáneas

#### Soluciones

**A. Usar Connection Pooling**
```python
# En requirements.txt
pgbouncer  # O psycopg2-pool

# En settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'erp_ventas_prod',
        'USER': 'erp_user',
        'PASSWORD': '***',
        'HOST': 'db',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # Reutilizar conexiones por 10 min
        'ATOMIC_REQUESTS': False,  # No abrir transacción por request
    }
}
```

**B. Ajustar worker processes de gunicorn**
```bash
# En Dockerfile o Dokploy:
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --threads 2 \
  --worker-class gthread \
  --max-requests 1000 \
  --max-requests-jitter 100
```

**C. Aumentar límite en PostgreSQL**
```sql
-- En psql:
ALTER SYSTEM SET max_connections = 200;
SELECT pg_reload_conf();
```

---

### 9. "Deadlock Detected"

#### Síntoma
```
psycopg2.extensions.TransactionRollbackError: deadlock detected
```

#### Causa
Dos transacciones compitiendo por los mismos recursos

#### Soluciones

**A. Usar transacciones con isolation level correcto**
```python
from django.db import transaction

@transaction.atomic(using='default', durable=True)
def procesar_pedido(pedido_id):
    pedido = Pedido.objects.select_for_update().get(id=pedido_id)
    # Tu lógica aquí
```

**B. Ordenar accesos a BD**
```python
# MALO (puede causar deadlock):
def crear_venta_mala(cliente_id, producto_id):
    cliente = Cliente.objects.get(id=cliente_id)  # Lock A
    producto = Producto.objects.get(id=producto_id)  # Lock B
    # Otra función hace Lock B luego Lock A -> DEADLOCK

# BUENO (no deadlock):
def crear_venta_buena(cliente_id, producto_id):
    # Siempre acceder en mismo orden (id menor primero)
    if cliente_id < producto_id:
        cliente = Cliente.objects.get(id=cliente_id)
        producto = Producto.objects.get(id=producto_id)
    else:
        producto = Producto.objects.get(id=producto_id)
        cliente = Cliente.objects.get(id=cliente_id)
```

---

### 10. "Stale Backup / Data Loss"

#### Síntoma
Backup tiene datos desactualizados cuando se necesita restaurar

#### Causas
- Backups no se ejecutan
- Backups se ejecutan pero se corrompen
- Sin verificación de integridad

#### Soluciones

**A. Verificar backups regularmente**
```bash
#!/bin/bash
# File: test_backups.sh

BACKUP_FILE=$1

# Verificar que existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo "✗ Backup file not found"
    exit 1
fi

# Verificar que no está vacío
if [ ! -s "$BACKUP_FILE" ]; then
    echo "✗ Backup file is empty"
    exit 1
fi

# Verificar integridad (uncompress test)
gzip -t "$BACKUP_FILE" && echo "✓ Backup integrity OK" || echo "✗ Backup is corrupted"

# Probar restauración en BD temporal
gunzip -c "$BACKUP_FILE" | psql -U erp_user -d test_erp_restore 2>&1 | tail -5
```

**B. Automatizar backup + test**
```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP="/mnt/backups/backup_$TIMESTAMP.sql.gz"

# Hacer backup
pg_dump -U erp_user -d erp_ventas_prod | gzip > "$BACKUP"

# Verificar integridad
if gzip -t "$BACKUP"; then
    echo "✓ Backup successful: $BACKUP"
    # Enviar a almacenamiento externo
    aws s3 cp "$BACKUP" s3://mi-bucket/backups/
else
    echo "✗ Backup corrupted!"
    exit 1
fi

# Eliminar backups > 7 días
find /mnt/backups -name "backup_*.sql.gz" -mtime +7 -delete
```

---

## ✅ Checklist Anti-Errores de BD

- [ ] PostgreSQL 15+ (no 12 o anteriores)
- [ ] Volumen persistente para `/var/lib/postgresql/data`
- [ ] Health check configurado en PostgreSQL
- [ ] `DB_WAIT_TIMEOUT` ≥ 300 segundos
- [ ] Migraciones resueltas localmente ANTES de deployar
- [ ] Datos de test (SEED) NO ejecutados en producción
- [ ] Backup automático configurado
- [ ] Backup verificado (no solo guardado)
- [ ] Conexión pooling habilitada
- [ ] Max connections ≥ 100
- [ ] Foreign keys en orden correcto
- [ ] No hay datos huérfanos (sin referencias válidas)
- [ ] Índices creados para queries frecuentes
- [ ] Logs monitoreados (no silenciados)
- [ ] Plan de recuperación ante desastre probado

