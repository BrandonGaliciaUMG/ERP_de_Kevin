from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.views.generic import TemplateView

from apps.clientes.models import Cliente
from apps.productos.models import Producto
from apps.pedidos.models import Pedido
from apps.ventas.models import Venta
from apps.reclamos.models import Reclamo


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        productos_bajo_stock = Producto.objects.filter(stock__lte=F('stock_minimo')).order_by('stock', 'nombre')
        context['totales'] = {
            'clientes': Cliente.objects.count(),
            'productos': Producto.objects.count(),
            'pedidos': Pedido.objects.count(),
            'ventas': Venta.objects.count(),
            'reclamos': Reclamo.objects.count(),
            'stock_bajo': productos_bajo_stock.count(),
        }
        context['pedidos_pendientes'] = Pedido.objects.filter(estado='pendiente').count()
        context['pedidos_entregados'] = Pedido.objects.filter(estado='entregado').count()
        context['reclamos_abiertos'] = Reclamo.objects.filter(estado='abierto').count()
        context['ultimos_pedidos'] = Pedido.objects.select_related('cliente').order_by('-fecha_pedido')[:5]
        context['ultimas_ventas'] = Venta.objects.select_related('pedido', 'pedido__cliente').order_by('-fecha_venta')[:5]
        context['ultimos_reclamos'] = Reclamo.objects.select_related('cliente', 'pedido').order_by('-fecha_creacion')[:5]
        context['alertas_stock'] = productos_bajo_stock[:5]
        return context
