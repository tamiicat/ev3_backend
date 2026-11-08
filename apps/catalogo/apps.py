from django.apps import AppConfig

class CatalogoConfig(AppConfig):
    # tipo de campo que Django usa por defecto para las claves primarias (id)
    default_auto_field = 'django.db.models.BigAutoField'
    # ruta completa de la app - "apps/", el nombre incluye ese prefijo (apps.catalogo y no solo catalogo).
    name = 'apps.catalogo'
    # nombre legible que se muestra en el panel de administración (/admin/)
    verbose_name = 'Catálogo de Paquetes Turísticos'
    