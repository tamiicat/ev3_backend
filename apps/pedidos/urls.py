from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('reservas/', views.carrito_ver, name='ver'),
    path('reservas/agregar/<int:id>/', views.carrito_agregar, name='agregar'),
    path('reservas/restar/<int:id>/', views.carrito_restar, name='restar'),
    path('reservas/eliminar/<int:id>/', views.carrito_eliminar, name='eliminar'),
    path('reservas/limpiar/', views.carrito_limpiar, name='limpiar'),
    path('checkout/', views.checkout_simulado, name='checkout'),
]