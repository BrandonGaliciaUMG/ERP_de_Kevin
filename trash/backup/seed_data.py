import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.clientes.models import Cliente
from apps.productos.models import Producto
from apps.pedidos.models import Pedido, DetallePedido
from apps.ventas.models import Venta
from apps.reclamos.models import Reclamo
from datetime import datetime, timedelta

# Crear Cliente de prueba
cliente = Cliente.objects.create(
    nombre="Acme Corporation",
    nit="123456789",
    telefono="+57 300 1234567",
    correo="contacto@acme.com",
    direccion="Calle Principal 123, Bogotá"
)
print(f"✅ Cliente creado: {cliente}")

# Crear Productos de prueba
productos = []
for i in range(3):
    prod = Producto.objects.create(
        nombre=f"Producto {i+1}",
        descripcion=f"Descripción del producto {i+1}",
        precio=100.00 * (i + 1),
        stock=50 - (i * 10),
        stock_minimo=5
    )
    productos.append(prod)
    print(f"✅ Producto creado: {prod}")

# Crear Pedido de prueba
pedido = Pedido.objects.create(
    cliente=cliente,
    fecha_entrega_estimada=datetime.now().date() + timedelta(days=7),
    estado='pendiente',
    observaciones='Pedido de prueba'
)
print(f"✅ Pedido creado: {pedido}")

# Crear Detalles de Pedido
for idx, prod in enumerate(productos):
    detalle = DetallePedido.objects.create(
        pedido=pedido,
        producto=prod,
        cantidad=2 + idx,
        precio_unitario=prod.precio
    )
    print(f"✅ Detalle Pedido creado: {detalle}")

# Calcular total del pedido
pedido.calcular_total()
print(f"✅ Total del pedido calculado: ${pedido.total}")

# Crear Venta de prueba
venta = Venta.objects.create(
    pedido=pedido,
    metodo_pago='tarjeta_credito',
    total=pedido.total,
    estado='pagada'
)
print(f"✅ Venta creada: {venta}")

# Crear Reclamo de prueba
reclamo = Reclamo.objects.create(
    cliente=cliente,
    pedido=pedido,
    descripcion="Producto llegó con defectos",
    estado='abierto'
)
print(f"✅ Reclamo creado: {reclamo}")

print("\n" + "="*50)
print("📊 RESUMEN DE DATOS DE PRUEBA")
print("="*50)
print(f"Clientes: {Cliente.objects.count()}")
print(f"Productos: {Producto.objects.count()}")
print(f"Pedidos: {Pedido.objects.count()}")
print(f"Ventas: {Venta.objects.count()}")
print(f"Reclamos: {Reclamo.objects.count()}")
print("="*50)
