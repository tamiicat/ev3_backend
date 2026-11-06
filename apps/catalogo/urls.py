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
    path('paquete/resena/<int:id>', views.guardar_resena, name='guardar_resena'),
]