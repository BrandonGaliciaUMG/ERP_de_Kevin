from django.urls import path
from .views import ClienteActivarView, ClienteCreateView, ClienteDetailView, ClienteInactivarView, ClienteListView, ClienteUpdateView

app_name = 'clientes'

urlpatterns = [
	path('', ClienteListView.as_view(), name='cliente_list'),
	path('crear/', ClienteCreateView.as_view(), name='cliente_create'),
	path('<int:pk>/', ClienteDetailView.as_view(), name='cliente_detail'),
	path('<int:pk>/editar/', ClienteUpdateView.as_view(), name='cliente_update'),
	path('<int:pk>/inactivar/', ClienteInactivarView.as_view(), name='cliente_inactivar'),
	path('<int:pk>/activar/', ClienteActivarView.as_view(), name='cliente_activar'),
]
