from django.contrib import admin
from .models import Venta

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'fecha_venta', 'metodo_pago', 'total', 'estado')
    list_filter = ('estado', 'metodo_pago', 'fecha_venta')
    search_fields = ('pedido__id', 'pedido__cliente__nombre')
    readonly_fields = ('pedido', 'fecha_venta', 'fecha_actualizacion', 'total')
    
    fieldsets = (
        ('Pedido', {
            'fields': ('pedido', 'total')
        }),
        ('Información de Pago', {
            'fields': ('metodo_pago', 'fecha_venta')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Fechas', {
            'fields': ('fecha_actualizacion',),
            'classes': ('collapse',)
        }),
    )
