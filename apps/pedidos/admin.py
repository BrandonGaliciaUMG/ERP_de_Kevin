from django.contrib import admin
from .models import Pedido, DetallePedido

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    readonly_fields = ('subtotal',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'estado', 'total', 'fecha_pedido', 'fecha_entrega_estimada')
    list_filter = ('estado', 'fecha_pedido', 'cliente')
    search_fields = ('cliente__nombre', 'id')
    readonly_fields = ('fecha_pedido', 'fecha_actualizacion', 'total')
    inlines = [DetallePedidoInline]
    
    fieldsets = (
        ('Cliente', {
            'fields': ('cliente',)
        }),
        ('Fechas', {
            'fields': ('fecha_pedido', 'fecha_entrega_estimada', 'fecha_entrega_real', 'fecha_actualizacion')
        }),
        ('Estado y Detalles', {
            'fields': ('estado', 'total', 'observaciones')
        }),
    )

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('fecha_creacion',)
    search_fields = ('pedido__id', 'producto__nombre')
    readonly_fields = ('subtotal', 'fecha_creacion')
