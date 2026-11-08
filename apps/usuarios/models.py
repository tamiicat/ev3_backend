from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Usuario(models.Model):
    # usuario del sitio (clientes y administradores)
    ROLES = [
        ('cliente', 'Cliente'),
        ('administrador', 'Administrador'),
    ]

    rut = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=12)
    correo_electronico = models.EmailField(unique=True)   # se usa como "usuario" para iniciar sesión
    # se guarda el HASH de la contraseña (nunca el texto original) - hash PBKDF2
    contrasena = models.CharField(max_length=128)
    rol = models.CharField(max_length=50, choices=ROLES, default='cliente')

    def set_password(self, contrasena_plana):
        self.contrasena = make_password(contrasena_plana)

    def check_password(self, contrasena_plana):
        return check_password(contrasena_plana, self.contrasena)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"