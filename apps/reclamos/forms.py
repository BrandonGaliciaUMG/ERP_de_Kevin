from django import forms
from .models import Reclamo


class ReclamoForm(forms.ModelForm):
    class Meta:
        model = Reclamo
        fields = ['cliente', 'pedido', 'descripcion', 'estado', 'resolucion']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'pedido': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows':3}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'resolucion': forms.Textarea(attrs={'class': 'form-control', 'rows':3}),
        }
