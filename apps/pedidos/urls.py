from django.urls import path
from .views import (
	PedidoListView, PedidoCreateView, PedidoUpdateView,
	PedidoDetailView, PedidoDeleteView,
)

app_name = 'pedidos'

urlpatterns = [
	path('', PedidoListView.as_view(), name='pedido_list'),
	path('nuevo/', PedidoCreateView.as_view(), name='pedido_create'),
	path('<int:pk>/', PedidoDetailView.as_view(), name='pedido_detail'),
	path('<int:pk>/editar/', PedidoUpdateView.as_view(), name='pedido_update'),
	path('<int:pk>/eliminar/', PedidoDeleteView.as_view(), name='pedido_delete'),
]
