from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'nit', 'telefono', 'correo', 'direccion', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo del cliente'}),
            'nit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIT o identificación fiscal'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono de contacto'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@empresa.com'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
