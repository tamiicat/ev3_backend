from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

class CategoriaDestino(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Continente o Región")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Categorías de Destino"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

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
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    categoria = models.ForeignKey(CategoriaDestino, on_delete=models.PROTECT, related_name="paquetes", null=True, verbose_name="Continente")
    descripcion = models.TextField()
    precio_paquete = models.FloatField()
    cupos_disponibles = models.IntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    imagen = models.ImageField(upload_to="paquetes/", blank=True, null=True, verbose_name="Imagen del Destino")
    activo = models.BooleanField(default=True, verbose_name="¿Activo?")

    hoteles = models.ManyToManyField(Hotel, related_name="paquetes", blank=True)
    vuelos = models.ManyToManyField(Vuelo, related_name="paquetes", blank=True)

    class Meta:
        verbose_name_plural = "Paquetes Turísticos"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nombre)
            slug = base_slug
            contador = 1
            while Paquete.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{contador}"
                contador += 1
            self.slug = slug
        super().save(*args, **kwargs)

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
    calificacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField()
    fecha_publicacion = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'paquete')
        ordering = ['-fecha_publicacion']

    def __str__(self):
        return f"Reseña de {self.usuario.nombre} para {self.paquete.nombre}"