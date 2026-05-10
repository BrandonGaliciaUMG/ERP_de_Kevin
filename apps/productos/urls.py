from django.urls import path
from .views import (
	ProductoListView, ProductoCreateView, ProductoUpdateView,
	ProductoDetailView, ProductoDeleteView,
)

app_name = 'productos'

urlpatterns = [
	path('', ProductoListView.as_view(), name='producto_list'),
	path('nuevo/', ProductoCreateView.as_view(), name='producto_create'),
	path('<int:pk>/', ProductoDetailView.as_view(), name='producto_detail'),
	path('<int:pk>/editar/', ProductoUpdateView.as_view(), name='producto_update'),
	path('<int:pk>/eliminar/', ProductoDeleteView.as_view(), name='producto_delete'),
]
