from django.db import models

class Hotel(models.Model):
    nombre = models.CharField(max_length=150)
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    categoria = models.CharField(max_length=50)
    habitacion = models.IntegerField()
    servicios = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Hoteles"

    def __str__(self):
        return f"{self.nombre} ({self.ciudad})"

class Vuelo(models.Model):
    aerolinea = models.CharField(max_length=100)
    ciudad_origen = models.CharField(max_length=100)
    ciudad_destino = models.CharField(max_length=100)
    fecha_salida = models.DateField()
    hora_salida = models.TimeField()
    fecha_llegada = models.DateField()
    hora_llegada = models.TimeField()

    def __str__(self):
        return f"{self.aerolinea}: {self.ciudad_origen} -> {self.ciudad_destino}"

class Paquete(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio_paquete = models.FloatField()
    cupos_disponibles = models.IntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    # tablas intermedias
    hoteles = models.ManyToManyField(Hotel, related_name="paquetes", blank=True)
    vuelos = models.ManyToManyField(Vuelo, related_name="paquetes", blank=True)

    def __str__(self):
        return self.nombre

class Itinerario(models.Model):
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE, related_name="itinerarios")
    dia = models.DateField()
    actividad = models.CharField(max_length=200)
    descripcion = models.TextField()
    horario = models.TimeField()

    def __str__(self):
        return f"{self.actividad} ({self.dia})"

class Resena(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE, related_name="resenas")
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE, related_name="resenas")
    calificacion = models.IntegerField()
    comentario = models.TextField()
    fecha_publicacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Reseña de {self.usuario.nombre} para {self.paquete.nombre}"