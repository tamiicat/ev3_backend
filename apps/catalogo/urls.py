from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.paquete_lista, name='lista'),
    path('paquete/<slug:slug>/', views.paquete_detalle, name='detalle'),
    path('gestion/', views.gestion_paquetes, name='gestion'),
    path('gestion/nueva/', views.paquete_crear, name='crear'),
    path('gestion/editar/<int:id>/', views.paquete_editar, name='editar'),
    path('gestion/eliminar/<int:id>/', views.paquete_eliminar, name='eliminar'),
]