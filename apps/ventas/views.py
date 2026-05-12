from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.permissions import RoleRequiredMixin

from .forms import VentaForm
from .models import Venta


class VentaListView(RoleRequiredMixin, ListView):
    allowed_roles = ('gerencia', 'ventas')
    model = Venta
    template_name = 'ventas/venta_list.html'
    context_object_name = 'ventas'
    paginate_by = 20

    def get_queryset(self):
        return Venta.objects.select_related('pedido', 'pedido__cliente').order_by('-fecha_venta')


class VentaCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ('gerencia', 'ventas')
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/venta_form.html'
    success_url = reverse_lazy('ventas:venta_list')

    def form_valid(self, form):
        messages.success(self.request, 'Venta creada correctamente.')
        return super().form_valid(form)


class VentaUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ('gerencia', 'ventas')
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/venta_form.html'
    success_url = reverse_lazy('ventas:venta_list')

    def form_valid(self, form):
        messages.success(self.request, 'Venta actualizada correctamente.')
        return super().form_valid(form)


class VentaDetailView(RoleRequiredMixin, DetailView):
    allowed_roles = ('gerencia', 'ventas')
    model = Venta
    template_name = 'ventas/venta_detail.html'
    context_object_name = 'venta'

    def get_queryset(self):
        return Venta.objects.select_related('pedido', 'pedido__cliente')


class VentaDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ('gerencia', 'ventas')
    model = Venta
    template_name = 'ventas/venta_confirm_delete.html'
    success_url = reverse_lazy('ventas:venta_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.estado = 'anulada'
        self.object.save(update_fields=['estado', 'fecha_actualizacion'])
        messages.success(request, f'La venta #{self.object.pk} fue anulada correctamente.')
        return redirect(self.success_url)
