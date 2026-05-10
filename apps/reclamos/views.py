from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Reclamo
from .forms import ReclamoForm


class ReclamoListView(LoginRequiredMixin, ListView):
    model = Reclamo
    template_name = 'reclamos/reclamo_list.html'
    context_object_name = 'reclamos'
    paginate_by = 20


class ReclamoCreateView(LoginRequiredMixin, CreateView):
    model = Reclamo
    form_class = ReclamoForm
    template_name = 'reclamos/reclamo_form.html'
    success_url = reverse_lazy('reclamos:reclamo_list')


class ReclamoUpdateView(LoginRequiredMixin, UpdateView):
    model = Reclamo
    form_class = ReclamoForm
    template_name = 'reclamos/reclamo_form.html'
    success_url = reverse_lazy('reclamos:reclamo_list')


class ReclamoDetailView(LoginRequiredMixin, DetailView):
    model = Reclamo
    template_name = 'reclamos/reclamo_detail.html'
    context_object_name = 'reclamo'


class ReclamoDeleteView(LoginRequiredMixin, DeleteView):
    model = Reclamo
    template_name = 'reclamos/reclamo_confirm_delete.html'
    success_url = reverse_lazy('reclamos:reclamo_list')
