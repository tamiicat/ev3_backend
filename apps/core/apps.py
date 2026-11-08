from django.apps import AppConfig

class CoreConfig(AppConfig):
    # tipo de campo por defecto para las claves primarias (id)
    default_auto_field = 'django.db.models.BigAutoField'
    # ruta completa de la app. Incluye el prefijo "apps." porque la app
    name = 'apps.core'
    verbose_name = 'Núcleo del Sitio'
    