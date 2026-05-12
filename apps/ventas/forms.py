from django import forms
from django.db.models import Q

from apps.pedidos.models import Pedido

from .models import Venta


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['pedido', 'metodo_pago', 'total', 'estado']
        widgets = {
            'pedido': forms.Select(attrs={'class': 'form-select'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-select'}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Pedido.objects.filter(venta__isnull=True)
        if self.instance and self.instance.pk:
            queryset = Pedido.objects.filter(Q(venta__isnull=True) | Q(pk=self.instance.pedido_id))
        self.fields['pedido'].queryset = queryset.select_related('cliente').order_by('-fecha_pedido')
