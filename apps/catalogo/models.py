from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

class CategoriaDestino(models.Model):
    # categoría o agrupación geográfica de los paquetes (África, Europa, Asia, etc.)..
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Continente o Región")
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categorías de Destino"   # plural correcto en el admin
        ordering = ['nombre']                           # orden alfabético por defecto

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        # si no se entregó slug, se genera automáticamente a partir del nombre.
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)  # guarda en la BD

class Hotel(models.Model):
    # hotel que puede incluirse en uno o varios paquetes.
    CATEGORIAS = [
        (1, '★ (1 estrella)'),
        (2, '★★ (2 estrellas)'),
        (3, '★★★ (3 estrellas)'),
        (4, '★★★★ (4 estrellas)'),
        (5, '★★★★★ (5 estrellas)'),
    ]

    nombre = models.CharField(max_length=150)
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    categoria = models.PositiveSmallIntegerField(choices=CATEGORIAS, default=3)  # 1 a 5 estrellas
    habitacion = models.IntegerField()              # cantidad de habitaciones del hotel
    servicios = models.BooleanField(default=False)  # ¿incluye servicios adicionales?

    class Meta:
        verbose_name_plural = "Hoteles"

    def __str__(self):
        return f"{self.nombre} ({self.ciudad})"

class Vuelo(models.Model):
    # vuelo disponible. Se asocia a los paquetes mediante la relación.
    aerolinea = models.CharField(max_length=100)
    ciudad_origen = models.CharField(max_length=100)
    ciudad_destino = models.CharField(max_length=100)
    # Fecha y hora se guardan por separado (DateField + TimeField).
    fecha_salida = models.DateField()
    hora_salida = models.TimeField()
    fecha_llegada = models.DateField()
    hora_llegada = models.TimeField()

    def __str__(self):
        return f"{self.aerolinea}: {self.ciudad_origen} -> {self.ciudad_destino}"

class Paquete(models.Model):
    # estado operativo del paquete (disponible, suspendido, agotado, en curso)
    ESTADOS_OPERATIVOS = [
        ('Disponible', 'Disponible'),
        ('Suspendido', 'Suspendido'),
        ('Agotado', 'Agotado'),
        ('En Curso', 'En Curso'),
    ]

    nombre = models.CharField(max_length=200)

    # slug único del paquete; se genera en save() si viene vacío.
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    # ForeignKey = cada paquete pertenece a UNA categoría (continente).
    categoria = models.ForeignKey(
        CategoriaDestino, on_delete=models.PROTECT,
        related_name="paquetes", null=True, verbose_name="Continente"
    )
    descripcion = models.TextField()

    # validación: el precio no puede ser negativo.
    precio_paquete = models.FloatField(validators=[MinValueValidator(0.0)])
    cupos_disponibles = models.IntegerField(validators=[MinValueValidator(0)])
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    estado = models.CharField(max_length=20, choices=ESTADOS_OPERATIVOS, default='Disponible')

    # ImageField: guarda la IMAGEN en disco (carpeta MEDIA_ROOT/paquetes/) y en la BD
    imagen = models.ImageField(upload_to="paquetes/", blank=True, null=True, verbose_name="Imagen del Destino")

    # "activo" controla la visibilidad pública: el catálogo solo muestra activo=True.
    activo = models.BooleanField(default=True, verbose_name="¿Activo?")

    # un paquete tiene varios hoteles/vuelos y un hotel/vuelo puede estar
    hoteles = models.ManyToManyField(Hotel, related_name="paquetes", blank=True)
    vuelos = models.ManyToManyField(Vuelo, related_name="paquetes", blank=True)

    class Meta:
        verbose_name_plural = "Paquetes Turísticos"
        ordering = ['-fecha_inicio']   # los más recientes primero por defecto

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        # genera un slug ÚNICO si el paquete aún no tiene uno.
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
    # una actividad dentro del itinerario de un paquete (una fila = una actividad).
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE, related_name="itinerarios")
    dia = models.DateField()                    # fecha en que ocurre la actividad
    actividad = models.CharField(max_length=200)
    descripcion = models.TextField()
    horario = models.TimeField()                # hora de inicio

    def __str__(self):
        return f"{self.actividad} ({self.dia})"

class Resena(models.Model):
    # reseña (calificación + comentario) que un usuario deja sobre un paquete.
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE, related_name="resenas")
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE, related_name="resenas")

    # restricción: entero positivo de 1-5 (estrellas).
    calificacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField()

    # auto_now_add=True: se completa solo con la fecha de creación y no se puede editar.
    fecha_publicacion = models.DateField(auto_now_add=True)

    class Meta:
        # restricción: un usuario solo puede tener UNA reseña por paquete
        unique_together = ('usuario', 'paquete')
        ordering = ['-fecha_publicacion'] # orden: reseñas más nuevas primero

    def __str__(self):
        return f"Reseña de {self.usuario.nombre} para {self.paquete.nombre}"