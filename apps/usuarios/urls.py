from django.urls import path
from .views import CustomLoginView, CustomLogoutView, RoleLoginView, role_login_action

app_name = 'usuarios'

urlpatterns = [
	path('login/', CustomLoginView.as_view(), name='login'),
	path('logout/', CustomLogoutView.as_view(), name='logout'),
	path('role-login/', RoleLoginView.as_view(), name='role_login'),
	path('role-login/<str:role>/', role_login_action, name='role_login_action'),
]
