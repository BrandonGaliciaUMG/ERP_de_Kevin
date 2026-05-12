# ERP de Ventas - MVP

Plataforma de gestion centralizada para ventas, pedidos, clientes, productos y reclamos.

## Tecnologias

- Python 3.11+
- Django 4.2
- Bootstrap 5
- SQLite para desarrollo local
- PostgreSQL preparado para Docker/produccion

## Estructura del Proyecto

```text
MVP/
├── apps/              # Aplicaciones Django
├── config/            # Configuracion principal de Django
├── static/            # Archivos estaticos fuente
├── templates/         # Templates HTML
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── requirements.txt
└── .env.example
```

## Levantar el Proyecto Localmente

Desde la carpeta raiz del proyecto:

```powershell
cd C:\Users\bogalicias\Desktop\MVP
```

1. Crear un entorno virtual:

```powershell
python -m venv .venv
```

2. Activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activacion por politicas de ejecucion, usar:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

3. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

4. Aplicar migraciones:

```powershell
python manage.py migrate
```

5. Crear datos de ejemplo, opcional:

```powershell
python manage.py seed --clients 20 --products 30
```

6. Levantar el servidor:

```powershell
python manage.py runserver
```

Abrir la aplicacion en:

```text
http://127.0.0.1:8000/
```

## Levantar con Docker

El entorno Docker usa PostgreSQL y crea usuarios/datos de ejemplo al iniciar por primera vez.

1. Opcional: copiar variables de ejemplo.

```powershell
Copy-Item .env.docker.example .env.docker
```

2. Construir y levantar contenedores:

```powershell
docker compose up --build
```

Si creas `.env.docker`, puedes usar:

```powershell
docker compose --env-file .env.docker up --build
```

Si no creas `.env.docker`, Docker Compose usara valores de desarrollo por defecto definidos en `docker-compose.yml`.

3. Abrir la aplicacion:

```text
http://127.0.0.1:8000/
```

4. Validar desde el contenedor:

```powershell
docker compose exec web python manage.py check
docker compose exec web python manage.py showmigrations
```

5. Reiniciar desde cero, borrando la base PostgreSQL de Docker:

```powershell
docker compose down -v
docker compose up --build
```

Para evitar recrear datos en cada arranque, configura `RUN_SEED=False` en `.env.docker` despues del primer inicio.

## Variables para Dokploy

Si Dokploy levanta este `docker-compose.yml` completo, incluyendo el servicio `db`, usa:

```env
WEB_PORT=8000
DOCKER_SECRET_KEY=una-clave-larga-segura
DOCKER_DEBUG=False
DOCKER_ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
DOCKER_CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com

POSTGRES_DB=erp_ventas_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=una-password-segura
DB_HOST=db
DB_PORT=5432
DB_WAIT_TIMEOUT=180

RUN_MIGRATIONS=True
RUN_COLLECTSTATIC=True
RUN_SEED=True
SEED_ONLY_IF_EMPTY=True
```

Si Dokploy usa una base PostgreSQL creada aparte, cambia `DB_HOST`, `DB_PORT`, `POSTGRES_DB`, `POSTGRES_USER` y `POSTGRES_PASSWORD` por los datos reales que entregue Dokploy. El error `failed to resolve host 'db'` o `Database db:5432 was not reachable in time` aparece cuando la app intenta conectarse a un host llamado `db` pero ese servicio no existe en la red del despliegue, o cuando Postgres no termino de aceptar conexiones dentro del tiempo de espera.

En Dokploy, `DB_HOST=db` solo es correcto si el servicio PostgreSQL se llama exactamente `db` dentro del mismo compose. Si creaste la base desde el panel de Dokploy, usa el hostname interno que muestra Dokploy para esa base, no `db`.

Si el log muestra:

```text
Database not ready yet: [Errno -3] Temporary failure in name resolution
```

el problema es DNS: el contenedor de Django no puede resolver el nombre configurado en `DB_HOST`. En ese caso:

- Si desplegaste solo el `Dockerfile`, no existe ningun servicio llamado `db`; crea una base PostgreSQL en Dokploy y usa su hostname interno en `DB_HOST`.
- Si desplegaste con `docker-compose.yml`, confirma que Dokploy este usando el compose completo y que el servicio se llame `db`.
- Si Dokploy muestra otro nombre interno para la base, usa ese valor exacto en `DB_HOST`.
- Como alternativa dentro del mismo compose, puedes probar `DB_HOST=erp_ventas_db`, que es el `container_name` definido para PostgreSQL.

Importante: `POSTGRES_USER`, `POSTGRES_DB` y `POSTGRES_PASSWORD` solo inicializan la base la primera vez que se crea el volumen PostgreSQL. Si el volumen ya existe, cambiar `POSTGRES_USER=erp_user` no crea ese usuario y Postgres mostrara `role "erp_user" does not exist`. En ese caso, usa el usuario con el que se creo el volumen o elimina/recrea el volumen si aun no hay datos reales.

Despues del primer despliegue con datos iniciales, cambia:

```env
RUN_SEED=False
```

Para HTTPS detras del proxy de Dokploy, conserva:

```env
SECURE_PROXY_SSL_HEADER=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

Cuando el dominio ya este funcionando en HTTPS, puedes endurecer seguridad con:

```env
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
```

## Credenciales Provisionales

Estas credenciales se crean/actualizan al ejecutar el comando `seed`:

- **admin** / `Admin@123`
- **gerencia** / `Gerencia@123`
- **ventas** / `Ventas@123`
- **inventario** / `Inventario@123`
- **test** / `Test@123`

## Comandos Utiles

Verificar configuracion del proyecto:

```powershell
python manage.py check
```

Crear un superusuario manualmente:

```powershell
python manage.py createsuperuser
```

Recolectar archivos estaticos para despliegue:

```powershell
python manage.py collectstatic
```
