from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView


class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = 'usuarios:login'


class RoleLoginView(TemplateView):
    """Pantalla informativa del acceso por rol deshabilitado."""
    template_name = 'usuarios/role_login.html'


def role_login_action(request, role):
    """Mantiene la ruta antigua pero no permite acceso automático por rol."""
    messages.info(request, 'El acceso por rol fue desactivado. Usa el login normal con usuario y contraseña.')
    return redirect('usuarios:login')
