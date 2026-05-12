from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.permissions import RoleRequiredMixin

from .forms import ProductoForm
from .models import Producto


class ProductoListView(RoleRequiredMixin, ListView):
    allowed_roles = ('gerencia', 'inventario')
    model = Producto
    template_name = 'productos/producto_list.html'
    context_object_name = 'productos'
    paginate_by = 20


class ProductoCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ('gerencia', 'inventario')
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('productos:producto_list')

    def form_valid(self, form):
        messages.success(self.request, 'Producto creado correctamente.')
        return super().form_valid(form)


class ProductoUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ('gerencia', 'inventario')
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('productos:producto_list')

    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado correctamente.')
        return super().form_valid(form)


class ProductoDetailView(RoleRequiredMixin, DetailView):
    allowed_roles = ('gerencia', 'inventario')
    model = Producto
    template_name = 'productos/producto_detail.html'
    context_object_name = 'producto'


class ProductoDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ('gerencia', 'inventario')
    model = Producto
    template_name = 'productos/producto_confirm_delete.html'
    success_url = reverse_lazy('productos:producto_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.estado = 'inactivo'
        self.object.save(update_fields=['estado', 'fecha_actualizacion'])
        messages.success(request, f'El producto "{self.object.nombre}" fue inactivado correctamente.')
        return redirect(self.success_url)
