from django.db.models import Count, F, Sum
from django.db.models.functions import TruncMonth
from django.views.generic import TemplateView

from apps.permissions import RoleRequiredMixin
from apps.clientes.models import Cliente
from apps.productos.models import Producto
from apps.pedidos.models import Pedido
from apps.ventas.models import Venta
from apps.reclamos.models import Reclamo


class DashboardView(RoleRequiredMixin, TemplateView):
    allowed_roles = ('gerencia',)
    template_name = 'dashboard/index.html'

    def _estado_chart(self, queryset, choices):
        counts = dict(queryset.values_list('estado').annotate(total=Count('id')))
        return {
            'labels': [label for value, label in choices],
            'values': [counts.get(value, 0) for value, label in choices],
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        productos_bajo_stock = Producto.objects.filter(stock__lte=F('stock_minimo')).order_by('stock', 'nombre')
        ventas_por_mes = (
            Venta.objects.annotate(mes=TruncMonth('fecha_venta'))
            .values('mes')
            .annotate(total=Sum('total'))
            .order_by('mes')
        )
        top_stock = Producto.objects.order_by('-stock', 'nombre')[:6]
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
        context['dashboard_charts'] = {
            'pedidos_estado': self._estado_chart(Pedido.objects.all(), Pedido.ESTADO_CHOICES),
            'ventas_estado': self._estado_chart(Venta.objects.all(), Venta.ESTADO_CHOICES),
            'reclamos_estado': self._estado_chart(Reclamo.objects.all(), Reclamo.ESTADO_CHOICES),
            'ventas_mes': {
                'labels': [item['mes'].strftime('%b %Y') for item in ventas_por_mes if item['mes']],
                'values': [float(item['total'] or 0) for item in ventas_por_mes if item['mes']],
            },
            'stock_productos': {
                'labels': [producto.nombre for producto in top_stock],
                'values': [producto.stock for producto in top_stock],
            },
        }
        return context
