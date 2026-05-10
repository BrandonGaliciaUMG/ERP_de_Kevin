from django import forms
from .models import Venta
from apps.pedidos.models import Pedido


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
        # por defecto mostrar pedidos que aún no tienen venta
        self.fields['pedido'].queryset = Pedido.objects.filter(venta__isnull=True)
