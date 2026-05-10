from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.apps import apps
from django.utils import timezone
import random


def has_field(model, fname):
    return fname in [f.name for f in model._meta.get_fields()]


def get_model(app_label, model_name):
    try:
        return apps.get_model(app_label, model_name)
    except Exception:
        return None


def fill_required_fields(model, pdata, context_instances=None):
    # context_instances: dict of model class -> list of instances for FK selection
    for field in model._meta.get_fields():
        if getattr(field, 'auto_created', False):
            continue
        if not getattr(field, 'editable', True):
            continue
        name = field.name
        # skip if already set
        if name in pdata:
            continue
        # only consider concrete fields
        if not hasattr(field, 'null'):
            continue
        if field.null or getattr(field, 'has_default', lambda: False)():
            continue
        internal = getattr(field, 'get_internal_type', lambda: lambda: None)()
        try:
            internal = field.get_internal_type()
        except Exception:
            internal = None

        # ForeignKey: try to pick an instance from context
        if internal == 'ForeignKey':
            rel_model = field.related_model
            if context_instances and rel_model in context_instances and context_instances[rel_model]:
                pdata[name] = random.choice(context_instances[rel_model])
            else:
                # skip if can't satisfy FK
                continue
        elif internal in ('DateTimeField', 'DateField'):
            pdata[name] = timezone.now() if internal == 'DateTimeField' else timezone.now().date()
        elif internal in ('CharField', 'TextField'):
            pdata[name] = 'n/a'
        elif internal in ('BooleanField',):
            pdata[name] = False
        elif internal in ('IntegerField', 'PositiveIntegerField', 'SmallIntegerField'):
            pdata[name] = 0
        elif internal in ('DecimalField', 'FloatField'):
            pdata[name] = 0
        else:
            # generic fallback
            pdata[name] = None


class Command(BaseCommand):
    help = 'Seed the database with example data (users, clients, products, pedidos, ventas, reclamos)'

    def add_arguments(self, parser):
        parser.add_argument('--clients', type=int, default=10, help='Number of clients to create')
        parser.add_argument('--products', type=int, default=10, help='Number of products to create')
        parser.add_argument('--orders', type=int, default=0, help='Number of pedidos to create')
        parser.add_argument('--sales', type=int, default=0, help='Number of ventas to create')
        parser.add_argument('--claims', type=int, default=0, help='Number of reclamos to create')

    def handle(self, *args, **options):
        self.stdout.write('Starting DB seed...')
        self.create_users()
        self.create_clients(options.get('clients', 10))
        self.create_products(options.get('products', 10))
        orders = options.get('orders', 0)
        sales = options.get('sales', 0)
        claims = options.get('claims', 0)
        if orders:
            self.create_orders(orders)
        if sales:
            self.create_sales(sales)
        if claims:
            self.create_claims(claims)
        self.stdout.write(self.style.SUCCESS('Seed finished.'))

    def create_users(self):
        User = get_user_model()
        users = [
            ('admin', 'Admin@123', True, True),
            ('gerencia', 'Gerencia@123', False, True),
            ('ventas', 'Ventas@123', False, True),
            ('inventario', 'Inventario@123', False, True),
            ('test', 'Test@123', False, True),
        ]

        for username, password, is_super, is_staff in users:
            obj, created = User.objects.get_or_create(username=username)
            if created:
                obj.is_superuser = is_super
                obj.is_staff = is_staff
            obj.set_password(password)
            obj.save()
            self.stdout.write(f"User '{username}' created/updated")

    def create_clients(self, n):
        Cliente = get_model('clientes', 'Cliente')
        if not Cliente:
            self.stdout.write('No model `Cliente` found; skipping clients seed.')
            return

        name_field = None
        email_field = None
        for f in ['nombre', 'name', 'full_name']:
            if has_field(Cliente, f):
                name_field = f
                break
        for f in ['email', 'correo']:
            if has_field(Cliente, f):
                email_field = f
                break

        nit_field = None
        for f in ['nit', 'ruc', 'identificacion']:
            if has_field(Cliente, f):
                nit_field = f
                break

        for i in range(n):
            name = f'Cliente {i+1}'
            email = f'cliente{i+1}@example.com'
            kwargs = {}
            if name_field:
                kwargs[name_field] = name
            if email_field:
                kwargs[email_field] = email
            if nit_field:
                kwargs[nit_field] = f'NIT-{i+1}-{random.randint(1000,9999)}'

            if not kwargs:
                self.stdout.write('Modelo Cliente no tiene campos compatibles; saltando creación')
                break

            try:
                obj, created = Cliente.objects.get_or_create(**kwargs)
                if created:
                    self.stdout.write(f'Created cliente: {name}')
            except Exception as e:
                self.stdout.write(f'Warning: could not create cliente {name}: {e}')
                continue

    def create_products(self, n):
        Producto = get_model('productos', 'Producto')
        if not Producto:
            self.stdout.write('No model `Producto` found; skipping products seed.')
            return

        name_field = None
        price_field = None
        stock_field = None
        for f in ['nombre', 'name']:
            if has_field(Producto, f):
                name_field = f
                break
        for f in ['precio', 'price']:
            if has_field(Producto, f):
                price_field = f
                break
        for f in ['stock', 'cantidad']:
            if has_field(Producto, f):
                stock_field = f
                break

        for i in range(n):
            name = f'Producto {i+1}'
            vals = {}
            if name_field:
                vals[name_field] = name
            if price_field:
                vals[price_field] = round(random.uniform(5.0, 200.0), 2)
            if stock_field:
                vals[stock_field] = random.randint(1, 100)

            if not vals:
                self.stdout.write('Modelo Producto no tiene campos compatibles; saltando creación')
                break

            defaults = {k: v for k, v in vals.items() if k != name_field}
            try:
                obj, created = Producto.objects.get_or_create(**{name_field: vals[name_field]}, defaults=defaults)
                if created:
                    self.stdout.write(f'Created producto: {name}')
                else:
                    # ensure other fields are updated
                    updated = False
                    for k, v in defaults.items():
                        if getattr(obj, k, None) != v:
                            setattr(obj, k, v)
                            updated = True
                    if updated:
                        obj.save()
            except Exception as e:
                self.stdout.write(f'Warning: could not create producto {name}: {e}')
                continue

    def create_orders(self, n):
        Pedido = get_model('pedidos', 'Pedido') or get_model('orders', 'Pedido')
        DetallePedido = get_model('pedidos', 'DetallePedido') or get_model('orders', 'DetallePedido')
        Cliente = get_model('clientes', 'Cliente')
        Producto = get_model('productos', 'Producto')

        if not Pedido or not Cliente or not Producto:
            self.stdout.write('No models `Pedido`/`Cliente`/`Producto` found; skipping pedidos seed.')
            return

        clientes = list(Cliente.objects.all())
        productos = list(Producto.objects.all())
        if not clientes or not productos:
            self.stdout.write('No clientes or productos available to create pedidos; skipping.')
            return

        # prepare context instances for FK defaults
        context = {Cliente: clientes, Producto: productos}
        for i in range(n):
            cliente = random.choice(clientes)
            pdata = {'cliente': cliente}
            # set fecha or created_at if present
            if has_field(Pedido, 'fecha') or has_field(Pedido, 'fecha_pedido'):
                key = 'fecha' if has_field(Pedido, 'fecha') else 'fecha_pedido'
                pdata[key] = timezone.now()
            # fill other required fields
            fill_required_fields(Pedido, pdata, context_instances=context)
            try:
                pedido = Pedido.objects.create(**pdata)
            except Exception as e:
                self.stdout.write(f'Warning: could not create pedido: {e}')
                continue
            # create detalle items
            if DetallePedido:
                # detect detalle field names
                det_pedido_fk = next((f for f in ['pedido', 'order', 'pedido_id'] if has_field(DetallePedido, f)), None)
                det_prod_fk = next((f for f in ['producto', 'product', 'producto_id'] if has_field(DetallePedido, f)), None)
                det_qty_field = next((f for f in ['cantidad', 'qty', 'cantidad_producto'] if has_field(DetallePedido, f)), None)
                det_price_field = next((f for f in ['precio_unitario', 'precio', 'price'] if has_field(DetallePedido, f)), None)

                for j in range(random.randint(1, 4)):
                    prod = random.choice(productos)
                    cantidad = max(1, random.randint(1, 10))
                    precio = getattr(prod, 'precio', getattr(prod, 'price', None))
                    if precio is None:
                        precio = round(random.uniform(5.0, 200.0), 2)
                    dkwargs = {}
                    if det_pedido_fk:
                        dkwargs[det_pedido_fk] = pedido
                    if det_prod_fk:
                        dkwargs[det_prod_fk] = prod
                    if det_qty_field:
                        dkwargs[det_qty_field] = cantidad
                    if det_price_field:
                        dkwargs[det_price_field] = precio
                    try:
                        DetallePedido.objects.create(**dkwargs)
                    except Exception as e:
                        self.stdout.write(f'Warning: could not create detalle pedido: {e}')
                        continue
                # recalculate pedido total if method available
                try:
                    pedido.calcular_total()
                except Exception:
                    pass
            self.stdout.write(f'Created pedido {pedido.pk} for cliente {cliente}')

    def create_sales(self, n):
        Venta = get_model('ventas', 'Venta') or get_model('sales', 'Venta')
        DetalleVenta = get_model('ventas', 'DetalleVenta') or get_model('sales', 'DetalleVenta')
        Cliente = get_model('clientes', 'Cliente')
        Producto = get_model('productos', 'Producto')
        Pedido = get_model('pedidos', 'Pedido') or get_model('orders', 'Pedido')

        if not Venta or not Cliente or not Producto:
            self.stdout.write('No models `Venta`/`Cliente`/`Producto` found; skipping ventas seed.')
            return

        clientes = list(Cliente.objects.all())
        productos = list(Producto.objects.all())
        if not clientes or not productos:
            self.stdout.write('No clientes or productos available to create ventas; skipping.')
            return

        context = {Cliente: clientes, Producto: productos}
        # try to find the FK field name that points to Cliente
        cliente_fk = None
        for f in Venta._meta.get_fields():
            if getattr(f, 'related_model', None) == Cliente:
                cliente_fk = f.name
                break
        # detect FK to Pedido if exists
        pedido_fk = None
        pedidos = list(Pedido.objects.all()) if Pedido else []
        # if ventas require a pedido FK and there are not enough pedidos,
        # create the missing pedidos so ventas can be created
        if Pedido and pedidos is not None and len(pedidos) < n:
            need = n - len(pedidos)
            self.stdout.write(f'Creating {need} additional pedidos to satisfy ventas')
            self.create_orders(need)
            pedidos = list(Pedido.objects.all())
        for f in Venta._meta.get_fields():
            if getattr(f, 'related_model', None) == Pedido:
                pedido_fk = f.name
                break

        for i in range(n):
            cliente = random.choice(clientes)
            vdata = {}
            pedido = None
            if cliente_fk:
                vdata[cliente_fk] = cliente
            if has_field(Venta, 'fecha'):
                vdata['fecha'] = timezone.now()
            if pedido_fk and pedidos:
                # assign a unique pedido to venta when Pedido <-> Venta is unique
                idx = random.randrange(len(pedidos))
                pedido = pedidos.pop(idx)
                vdata[pedido_fk] = pedido
            if pedido is not None and has_field(Venta, 'total'):
                vdata['total'] = getattr(pedido, 'total', 0) or 0
            fill_required_fields(Venta, vdata, context_instances=context)
            try:
                venta = Venta.objects.create(**vdata)
            except Exception as e:
                self.stdout.write(f'Warning: could not create venta: {e}')
                continue
            if DetalleVenta:
                # detect det_venta_fk, qty and price field names once
                det_venta_fk = None
                for f in ['venta', 'sale', 'venta_id']:
                    if has_field(DetalleVenta, f):
                        det_venta_fk = f
                        break
                det_qty_field = next((f for f in ['cantidad', 'qty', 'cantidad_producto'] if has_field(DetalleVenta, f)), None)
                det_price_field = next((f for f in ['precio', 'price'] if has_field(DetalleVenta, f)), None)

                for j in range(random.randint(1, 4)):
                    prod = random.choice(productos)
                    cantidad = max(1, random.randint(1, 10))
                    precio = getattr(prod, 'precio', getattr(prod, 'price', None))
                    if precio is None:
                        precio = round(random.uniform(5.0, 200.0), 2)
                    dkwargs = {}
                    if det_venta_fk:
                        dkwargs[det_venta_fk] = venta
                    for pk in ['producto', 'product', 'producto_id']:
                        if has_field(DetalleVenta, pk):
                            dkwargs[pk] = prod
                            break
                    if det_qty_field:
                        dkwargs[det_qty_field] = cantidad
                    if det_price_field:
                        dkwargs[det_price_field] = precio
                    try:
                        DetalleVenta.objects.create(**dkwargs)
                    except Exception:
                        continue
            self.stdout.write(f'Created venta {venta.pk} for cliente {cliente}')


    def create_claims(self, n):
        Reclamo = get_model('reclamos', 'Reclamo') or get_model('claims', 'Reclamo')
        Cliente = get_model('clientes', 'Cliente')
        Pedido = get_model('pedidos', 'Pedido') or get_model('orders', 'Pedido')
        Producto = get_model('productos', 'Producto')

        if not Reclamo or not Cliente:
            self.stdout.write('No models `Reclamo`/`Cliente` found; skipping reclamos seed.')
            return

        clientes = list(Cliente.objects.all())
        pedidos = list(Pedido.objects.all()) if Pedido else []
        productos = list(Producto.objects.all()) if Producto else []

        context = {Cliente: clientes, Producto: productos} if productos else {Cliente: clientes}
        # detect FK names for cliente and producto on Reclamo
        cliente_fk = None
        producto_fk = None
        for f in Reclamo._meta.get_fields():
            if getattr(f, 'related_model', None) == Cliente:
                cliente_fk = f.name
            if Producto and getattr(f, 'related_model', None) == Producto:
                producto_fk = f.name

        for i in range(n):
            cliente = random.choice(clientes)
            data = {}
            if cliente_fk:
                data[cliente_fk] = cliente
            pedido_fk = next((f.name for f in Reclamo._meta.get_fields() if getattr(f, 'related_model', None) == Pedido), None) if Pedido else None
            if Pedido and pedidos and pedido_fk:
                pedidos_cliente = [p for p in pedidos if getattr(p, 'cliente_id', None) == cliente.id]
                pedido_elegido = random.choice(pedidos_cliente or pedidos)
                data[pedido_fk] = pedido_elegido
            if productos and producto_fk:
                data[producto_fk] = random.choice(productos)
            # set descripcion if present
            for f in ['descripcion', 'descripcion_reclamo', 'detail']:
                if has_field(Reclamo, f):
                    data[f] = f'Reclamo de prueba {i+1}'
                    break
            # estado
            for s in ['estado', 'status']:
                if has_field(Reclamo, s):
                    data[s] = 'abierto'
                    break
            fill_required_fields(Reclamo, data, context_instances=context)
            try:
                obj = Reclamo.objects.create(**data)
                self.stdout.write(f'Created reclamo {obj.pk} for cliente {cliente}')
            except Exception as e:
                self.stdout.write(f'Warning: could not create reclamo: {e}')
                continue
