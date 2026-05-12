from django.urls import path
from .views import (
	VentaListView, VentaCreateView, VentaUpdateView,
	VentaDetailView, VentaDeleteView,
)

app_name = 'ventas'

urlpatterns = [
	path('', VentaListView.as_view(), name='venta_list'),
	path('nuevo/', VentaCreateView.as_view(), name='venta_create'),
	path('<int:pk>/', VentaDetailView.as_view(), name='venta_detail'),
	path('<int:pk>/editar/', VentaUpdateView.as_view(), name='venta_update'),
	path('<int:pk>/eliminar/', VentaDeleteView.as_view(), name='venta_delete'),
]
