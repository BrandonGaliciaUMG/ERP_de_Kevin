from django.contrib.auth.models import User

u = User.objects.get(username='admin')
u.set_password('Admin@123')
u.save()
print(f"Contraseña actualizada para {u.username}")
