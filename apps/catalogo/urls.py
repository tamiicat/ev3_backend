from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.paquete_lista, name='lista'),
    path('paquete/<int:id>/', views.paquete_detalle, name='detalle'),
    path('gestion/', views.gestion_paquetes, name='gestion'),
    path('gestion/nueva/', views.paquete_crear, name='crear'),
    path('gestion/editar/<int:id>/', views.paquete_editar, name='editar'),
    path('gestion/eliminar/<int:id>/', views.paquete_eliminar, name='eliminar'),
    path('gestion-itinerario/', views.gestion_itinerario, name='gestion_itinerario'),
    path('gestion-itinerario/nuevo/', views.itinerario_crear, name='itinerario_crear'),
    path('gestion-itinerario/editar/<int:id>/', views.itinerario_editar, name='itinerario_editar'),
    path('gestion-itinerario/eliminar/<int:id>/', views.itinerario_eliminar, name='itinerario_eliminar'),
    path('paquete/<int:id>/resena/', views.guardar_resena, name='guardar_resena'),
    path('gestion-hotel/', views.gestion_hotel, name='gestion_hotel'),
    path('gestion-hotel/nuevo/', views.hotel_crear, name='hotel_crear'),
    path('gestion-hotel/editar/<int:id>/', views.hotel_editar, name='hotel_editar'),
    path('gestion-hotel/eliminar/<int:id>/', views.hotel_eliminar, name='hotel_eliminar'),
    path('gestion-vuelo/', views.gestion_vuelo, name='gestion_vuelo'),
    path('gestion-vuelo/nuevo/', views.vuelo_crear, name='vuelo_crear'),
    path('gestion-vuelo/editar/<int:id>/', views.vuelo_editar, name='vuelo_editar'),
    path('gestion-vuelo/eliminar/<int:id>/', views.vuelo_eliminar, name='vuelo_eliminar'),
]