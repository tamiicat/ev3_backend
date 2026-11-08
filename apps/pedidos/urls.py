from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('reservas/', views.carrito_ver, name='ver'),                               # ver el carrito
    path('reservas/agregar/<int:id>/', views.carrito_agregar, name='agregar'),      # +1 unidad
    path('reservas/restar/<int:id>/', views.carrito_restar, name='restar'),         # -1 unidad
    path('reservas/eliminar/<int:id>/', views.carrito_eliminar, name='eliminar'),   # quitar el paquete
    path('reservas/limpiar/', views.carrito_limpiar, name='limpiar'),               # vaciar el carrito
    path('checkout/', views.checkout_simulado, name='checkout'),                    # pagar (simulado)
]