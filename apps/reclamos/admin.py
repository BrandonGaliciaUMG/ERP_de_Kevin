from django.contrib import admin
from .models import Reclamo

@admin.register(Reclamo)
class ReclamoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'pedido', 'estado', 'fecha_creacion', 'fecha_resolucion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('cliente__nombre', 'pedido__id', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Cliente y Pedido', {
            'fields': ('cliente', 'pedido')
        }),
        ('Descripción del Reclamo', {
            'fields': ('descripcion',)
        }),
        ('Resolución', {
            'fields': ('estado', 'resolucion', 'fecha_resolucion')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
