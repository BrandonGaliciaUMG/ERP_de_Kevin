from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.permissions import RoleRequiredMixin

from .forms import ReclamoForm
from .models import Reclamo


class ReclamoListView(RoleRequiredMixin, ListView):
    allowed_roles = ('gerencia', 'ventas', 'inventario')
    model = Reclamo
    template_name = 'reclamos/reclamo_list.html'
    context_object_name = 'reclamos'
    paginate_by = 20

    def get_queryset(self):
        return Reclamo.objects.select_related('cliente', 'pedido').order_by('-fecha_creacion')


class ReclamoCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ('gerencia', 'ventas', 'inventario')
    model = Reclamo
    form_class = ReclamoForm
    template_name = 'reclamos/reclamo_form.html'
    success_url = reverse_lazy('reclamos:reclamo_list')

    def form_valid(self, form):
        messages.success(self.request, 'Reclamo creado correctamente.')
        return super().form_valid(form)


class ReclamoUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ('gerencia', 'ventas', 'inventario')
    model = Reclamo
    form_class = ReclamoForm
    template_name = 'reclamos/reclamo_form.html'
    success_url = reverse_lazy('reclamos:reclamo_list')

    def form_valid(self, form):
        if form.instance.estado in {'resuelto', 'cerrado'} and not form.instance.fecha_resolucion:
            form.instance.fecha_resolucion = timezone.now()
        messages.success(self.request, 'Reclamo actualizado correctamente.')
        return super().form_valid(form)


class ReclamoDetailView(RoleRequiredMixin, DetailView):
    allowed_roles = ('gerencia', 'ventas', 'inventario')
    model = Reclamo
    template_name = 'reclamos/reclamo_detail.html'
    context_object_name = 'reclamo'

    def get_queryset(self):
        return Reclamo.objects.select_related('cliente', 'pedido')


class ReclamoCambiarEstadoView(RoleRequiredMixin, View):
    allowed_roles = ('gerencia', 'ventas', 'inventario')

    def post(self, request, pk, estado):
        estados_validos = {value for value, label in Reclamo.ESTADO_CHOICES}
        if estado not in estados_validos:
            return HttpResponseBadRequest('Estado de reclamo no valido.')

        reclamo = get_object_or_404(Reclamo, pk=pk)
        reclamo.estado = estado
        update_fields = ['estado', 'fecha_actualizacion']
        if estado in {'resuelto', 'cerrado'} and not reclamo.fecha_resolucion:
            reclamo.fecha_resolucion = timezone.now()
            update_fields.append('fecha_resolucion')
        elif estado in {'abierto', 'en_revision'}:
            reclamo.fecha_resolucion = None
            update_fields.append('fecha_resolucion')
        reclamo.save(update_fields=update_fields)
        messages.success(request, f'El reclamo #{reclamo.pk} cambió a {reclamo.get_estado_display()}.')
        return redirect('reclamos:reclamo_list')


class ReclamoDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ('gerencia', 'ventas', 'inventario')
    model = Reclamo
    template_name = 'reclamos/reclamo_confirm_delete.html'
    success_url = reverse_lazy('reclamos:reclamo_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.estado = 'cerrado'
        if not self.object.fecha_resolucion:
            self.object.fecha_resolucion = timezone.now()
        self.object.save(update_fields=['estado', 'fecha_resolucion', 'fecha_actualizacion'])
        messages.success(request, f'El reclamo #{self.object.pk} fue cerrado correctamente.')
        return redirect(self.success_url)
