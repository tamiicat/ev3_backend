from django.db import models

class Usuario(models.Model):
    ROLES = [
        ('cliente', 'Cliente'),
        ('administrador', 'Administrador'),
    ]

    rut = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.IntegerField()
    correo_electronico = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=128)
    rol = models.CharField(max_length=50, choices=ROLES, default='cliente')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"