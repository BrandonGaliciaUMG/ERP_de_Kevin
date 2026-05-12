from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.permissions import RoleRequiredMixin

from .forms import DetallePedidoFormSet, PedidoForm
from .models import Pedido


class PedidoListView(RoleRequiredMixin, ListView):
    allowed_roles = ('gerencia', 'ventas')
    model = Pedido
    template_name = 'pedidos/pedido_list.html'
    context_object_name = 'pedidos'
    paginate_by = 20

    def get_queryset(self):
        return Pedido.objects.select_related('cliente').order_by('-fecha_pedido')


class PedidoFormSetMixin(RoleRequiredMixin):
    allowed_roles = ('gerencia', 'ventas')
    model = Pedido
    form_class = PedidoForm
    template_name = 'pedidos/pedido_form.html'
    success_url = reverse_lazy('pedidos:pedido_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detalle_formset'] = DetallePedidoFormSet(self.request.POST, instance=self.object)
        else:
            context['detalle_formset'] = DetallePedidoFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data(form=form)
        detalle_formset = context['detalle_formset']
        if not detalle_formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            self.object = form.save()
            detalle_formset.instance = self.object
            detalle_formset.save()
            self.object.calcular_total()
        messages.success(self.request, 'Pedido guardado correctamente.')
        return redirect(self.get_success_url())


class PedidoCreateView(PedidoFormSetMixin, CreateView):
    pass


class PedidoUpdateView(PedidoFormSetMixin, UpdateView):
    pass


class PedidoDetailView(RoleRequiredMixin, DetailView):
    allowed_roles = ('gerencia', 'ventas')
    model = Pedido
    template_name = 'pedidos/pedido_detail.html'
    context_object_name = 'pedido'

    def get_queryset(self):
        return Pedido.objects.select_related('cliente').prefetch_related('detalles__producto')


class PedidoDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ('gerencia', 'ventas')
    model = Pedido
    template_name = 'pedidos/pedido_confirm_delete.html'
    success_url = reverse_lazy('pedidos:pedido_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.estado = 'cancelado'
        self.object.save(update_fields=['estado', 'fecha_actualizacion'])
        messages.success(request, f'El pedido #{self.object.pk} fue cancelado correctamente.')
        return redirect(self.success_url)
