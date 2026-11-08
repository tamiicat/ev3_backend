from django.apps import AppConfig

# configuración estándar de la app; se registra en INSTALLED_APPS como 'apps.usuarios'
class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'
    verbose_name = 'Usuarios y Clientes'