from django.urls import path
from .views import (
	ReclamoListView, ReclamoCreateView, ReclamoUpdateView,
	ReclamoDetailView, ReclamoDeleteView, ReclamoCambiarEstadoView,
)

app_name = 'reclamos'

urlpatterns = [
	path('', ReclamoListView.as_view(), name='reclamo_list'),
	path('nuevo/', ReclamoCreateView.as_view(), name='reclamo_create'),
	path('<int:pk>/', ReclamoDetailView.as_view(), name='reclamo_detail'),
	path('<int:pk>/editar/', ReclamoUpdateView.as_view(), name='reclamo_update'),
	path('<int:pk>/estado/<str:estado>/', ReclamoCambiarEstadoView.as_view(), name='reclamo_cambiar_estado'),
	path('<int:pk>/eliminar/', ReclamoDeleteView.as_view(), name='reclamo_delete'),
]
