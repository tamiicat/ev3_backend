from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    # parte pública del catálogo
    path('', views.paquete_lista, name='lista'),                                  # listado con búsqueda, filtros y paginación
    path('paquete/<int:id>/', views.paquete_detalle, name='detalle'),             # detalle de un paquete

    # gestión de paquetes (solo administradores)
    path('gestion/', views.gestion_paquetes, name='gestion'),                     # tabla de administración
    path('gestion/nueva/', views.paquete_crear, name='crear'),                    # formulario de creación
    path('gestion/editar/<int:id>/', views.paquete_editar, name='editar'),        # formulario de edición
    path('gestion/eliminar/<int:id>/', views.paquete_eliminar, name='eliminar'),  # confirmación y borrado

    # gestión de itinerarios (solo administradores) 
    path('gestion-itinerario/', views.gestion_itinerario, name='gestion_itinerario'),
    path('gestion-itinerario/nuevo/', views.itinerario_crear, name='itinerario_crear'),
    path('gestion-itinerario/editar/<int:id>/', views.itinerario_editar, name='itinerario_editar'),
    path('gestion-itinerario/eliminar/<int:id>/', views.itinerario_eliminar, name='itinerario_eliminar'),

    # reseñas (usuarios con sesión que pagaron el paquete)
    path('paquete/<int:id>/resena/', views.guardar_resena, name='guardar_resena'),

    # gestión de hoteles (solo administradores)
    path('gestion-hotel/', views.gestion_hotel, name='gestion_hotel'),
    path('gestion-hotel/nuevo/', views.hotel_crear, name='hotel_crear'),
    path('gestion-hotel/editar/<int:id>/', views.hotel_editar, name='hotel_editar'),
    path('gestion-hotel/eliminar/<int:id>/', views.hotel_eliminar, name='hotel_eliminar'),

    # gestión de vuelos (solo administradores)
    path('gestion-vuelo/', views.gestion_vuelo, name='gestion_vuelo'),
    path('gestion-vuelo/nuevo/', views.vuelo_crear, name='vuelo_crear'),
    path('gestion-vuelo/editar/<int:id>/', views.vuelo_editar, name='vuelo_editar'),
    path('gestion-vuelo/eliminar/<int:id>/', views.vuelo_eliminar, name='vuelo_eliminar'),
]