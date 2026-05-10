import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.clientes.models import Cliente
from apps.productos.models import Producto
from apps.pedidos.models import Pedido, DetallePedido
from apps.ventas.models import Venta
from apps.reclamos.models import Reclamo

print("="*60)
print("📊 PASO 3: VERIFICACIÓN DE MODELOS Y DATOS")
print("="*60)

# Verificar modelos
print("\n✅ MODELOS CREADOS:")
print(f"  - Cliente: {Cliente._meta.get_fields()}")
print(f"  - Producto: {Producto._meta.get_fields()}")  
print(f"  - Pedido: {Pedido._meta.get_fields()}")
print(f"  - DetallePedido: {DetallePedido._meta.get_fields()}")
print(f"  - Venta: {Venta._meta.get_fields()}")
print(f"  - Reclamo: {Reclamo._meta.get_fields()}")

# Verificar datos
print("\n✅ DATOS EN BASE DE DATOS:")
print(f"  - Clientes: {Cliente.objects.count()} registros")
print(f"  - Productos: {Producto.objects.count()} registros")
print(f"  - Pedidos: {Pedido.objects.count()} registros")
print(f"  - Detalles Pedido: {DetallePedido.objects.count()} registros")
print(f"  - Ventas: {Venta.objects.count()} registros")
print(f"  - Reclamos: {Reclamo.objects.count()} registros")

# Listar datos específicos
print("\n✅ LISTA DE CLIENTES:")
for cliente in Cliente.objects.all():
    print(f"  - {cliente.nombre} ({cliente.nit}) - Estado: {cliente.estado}")

print("\n✅ LISTA DE PRODUCTOS:")
for prod in Producto.objects.all():
    print(f"  - {prod.nombre} - ${prod.precio} - Stock: {prod.stock}")

print("\n✅ LISTA DE PEDIDOS:")
for pedido in Pedido.objects.all():
    print(f"  - Pedido #{pedido.id} - {pedido.cliente.nombre} - Total: ${pedido.total} - Estado: {pedido.estado}")

print("\n✅ LISTA DE VENTAS:")
for venta in Venta.objects.all():
    print(f"  - Venta #{venta.id} - ${venta.total} - Método: {venta.metodo_pago} - Estado: {venta.estado}")

print("\n✅ LISTA DE RECLAMOS:")
for reclamo in Reclamo.objects.all():
    print(f"  - Reclamo #{reclamo.id} - {reclamo.cliente.nombre} - Estado: {reclamo.estado}")

print("\n" + "="*60)
print("✅ PASO 3 COMPLETADO: TODOS LOS MODELOS FUNCIONAN CORRECTAMENTE")
print("="*60)
