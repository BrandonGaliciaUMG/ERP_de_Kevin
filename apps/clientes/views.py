from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ClienteForm
from .models import Cliente


class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'clientes/cliente_list.html'
    context_object_name = 'clientes'
    ordering = ['-fecha_registro']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q', '').strip()
        estado = self.request.GET.get('estado', '').strip()

        if query:
            queryset = queryset.filter(
                nombre__icontains=query
            ) | queryset.filter(
                nit__icontains=query
            ) | queryset.filter(
                correo__icontains=query
            )

        if estado in {'activo', 'inactivo', 'suspendido'}:
            queryset = queryset.filter(estado=estado)

        return queryset.distinct().order_by('-fecha_registro')


class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = 'clientes/cliente_detail.html'
    context_object_name = 'cliente'


class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:cliente_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente creado correctamente.')
        return super().form_valid(form)


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:cliente_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente actualizado correctamente.')
        return super().form_valid(form)


class ClienteInactivarView(LoginRequiredMixin, View):
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        cliente.estado = 'inactivo'
        cliente.save(update_fields=['estado', 'fecha_actualizacion'])
        messages.success(request, f'El cliente {cliente.nombre} fue inactivado correctamente.')
        return redirect('clientes:cliente_list')


class ClienteActivarView(LoginRequiredMixin, View):
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        cliente.estado = 'activo'
        cliente.save(update_fields=['estado', 'fecha_actualizacion'])
        messages.success(request, f'El cliente {cliente.nombre} fue reactivado correctamente.')
        return redirect('clientes:cliente_list')
