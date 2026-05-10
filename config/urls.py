from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('clientes/', include('apps.clientes.urls')),
    path('productos/', include('apps.productos.urls')),
    path('pedidos/', include('apps.pedidos.urls')),
    path('ventas/', include('apps.ventas.urls')),
    path('reclamos/', include('apps.reclamos.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
