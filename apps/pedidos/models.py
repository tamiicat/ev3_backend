from django.db import models

class Reserva(models.Model):
    # una reserva: un usuario compra un paquete con las opciones que eligió
    # PROTECT: no se puede borrar un usuario o paquete que tenga reservas.
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.PROTECT, related_name="reservas")
    paquete = models.ForeignKey('catalogo.Paquete', on_delete=models.PROTECT, related_name="reservas")
    fecha = models.DateField(auto_now_add=True)       # fecha de creación, automática
    # para saber si el usuario puede reseñar el paquete.
    estado = models.CharField(max_length=50)
    precio_total = models.FloatField()                # incluye IVA (ver checkout_simulado)

    # selección del cliente dentro del paquete (actividades, hotel y vuelo elegidos).
    actividades = models.ManyToManyField('catalogo.Itinerario', blank=True, related_name='reservas')
    hoteles = models.ManyToManyField('catalogo.Hotel', blank=True, related_name='reservas')
    vuelos = models.ManyToManyField('catalogo.Vuelo', blank=True, related_name='reservas')

    def __str__(self):
        return f"Reserva {self.pk} - {self.usuario.nombre}"

class Pago(models.Model):
    # un pago asociado a una reserva
    reserva = models.ForeignKey(Reserva, on_delete=models.PROTECT, related_name="pagos")
    monto = models.FloatField()
    metodo_pago = models.CharField(max_length=100)         
    fecha_hora_pago = models.DateTimeField(auto_now_add=True)
    estado_transaccion = models.CharField(max_length=50)  

    def __str__(self):
        return f"Pago {self.pk} - Reserva {self.reserva.pk}"