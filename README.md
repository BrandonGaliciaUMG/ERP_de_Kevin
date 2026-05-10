# MVP - ERP Ventas

Credenciales provisionales (puede moverlas o eliminarlas después):

- **admin** / `Admin@123`
- **gerencia** / `Gerencia@123`
- **ventas** / `Ventas@123`
- **inventario** / `Inventario@123`
- **test** / `Test@123`

Cómo ejecutar el comando de seeds que añadimos:

1. Activar el virtualenv del proyecto.

```powershell
.\venv\Scripts\Activate.ps1
```

2. Ejecutar el comando `seed` para crear datos de ejemplo (opcionalmente ajustar cantidades):

```powershell
python manage.py seed --clients 20 --products 30
```

El comando intenta crear usuarios y datos básicos (clientes, productos). Si tu proyecto tiene modelos con nombres distintos, revisa el fichero [apps/usuarios/management/commands/seed.py](apps/usuarios/management/commands/seed.py) y adáptalo.

---
Fecha: 2026-05-03
# ERP de Ventas - MVP

## Descripción
Plataforma de gestión centralizada para ventas, pedidos, clientes y reclamos.

## Estado del Desarrollo
Proyecto en construcción - PASO 1 completado.

## Tecnologías
- Python 3.11
- Django 4.2
- PostgreSQL 15
- Docker & Docker Compose
- Bootstrap 5

## Estructura del Proyecto
```
erp_ventas/
├── config/           # Configuración de Django
├── apps/             # Aplicaciones modulares
├── templates/        # Templates HTML
├── static/          # Archivos estáticos
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── requirements.txt
└── .env.example
```

## Pasos Completados
✅ PASO 1: Estructura base + archivos iniciales

## Próximos Pasos
⏳ PASO 2: Crear apps Django funcionales
⏳ PASO 3: Definir modelos de BD
⏳ PASO 4: Implementar CRUD Cliente
