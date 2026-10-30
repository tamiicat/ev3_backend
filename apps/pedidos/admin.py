from django.contrib import admin
from .models import Reserva, Pago

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'paquete', 'fecha', 'estado', 'precio_total')
    list_filter = ('estado', 'fecha')
    search_fields = ('usuario__nombre', 'usuario__rut', 'paquete__nombre', 'estado')
    list_editable = ('estado',)
    list_per_page = 20

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'reserva', 'monto', 'metodo_pago', 'estado_transaccion', 'fecha_hora_pago')
    list_filter = ('metodo_pago', 'estado_transaccion', 'fecha_hora_pago')
    search_fields = ('reserva__id', 'metodo_pago', 'estado_transaccion')
    list_editable = ('estado_transaccion',)
    list_per_page = 20