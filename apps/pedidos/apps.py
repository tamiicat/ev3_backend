from django.apps import AppConfig

class PedidosConfig(AppConfig):
    # tipo de clave primaria por defecto
    default_auto_field = 'django.db.models.BigAutoField'  
    # ruta de la app (incluye el prefijo apps.)
    name = 'apps.pedidos'                                 
    verbose_name = 'Pedidos y Carrito de Compras'           
    