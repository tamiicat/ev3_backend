from django.db import models

class Reserva(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.PROTECT, related_name="reservas")
    paquete = models.ForeignKey('catalogo.Paquete', on_delete=models.PROTECT, related_name="reservas")
    fecha = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=50)
    precio_total = models.FloatField()

    def __str__(self):
        return f"Reserva {self.pk} - {self.usuario.nombre}"

class Pago(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.PROTECT, related_name="pagos")
    monto = models.FloatField()
    metodo_pago = models.CharField(max_length=100)
    fecha_hora_pago = models.DateTimeField(auto_now_add=True)
    estado_transaccion = models.CharField(max_length=50)

    def __str__(self):
        return f"Pago {self.pk} - Reserva {self.reserva.pk}"