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
