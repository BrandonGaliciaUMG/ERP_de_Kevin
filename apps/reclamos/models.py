from django.db import models
from apps.clientes.models import Cliente
from apps.pedidos.models import Pedido

class Reclamo(models.Model):
    ESTADO_CHOICES = [
        ('abierto', 'Abierto'),
        ('en_revision', 'En revisión'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='reclamos')
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True, blank=True, related_name='reclamos')
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='abierto')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    resolucion = models.TextField(blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Reclamo"
        verbose_name_plural = "Reclamos"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Reclamo {self.id} - {self.cliente.nombre} ({self.estado})"
