from django.contrib.auth.hashers import make_password, identify_hasher
from django.core.management.base import BaseCommand

from apps.usuarios.models import Usuario

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        cifradas = 0
        omitidas = 0

        for usuario in Usuario.objects.all():
            try:
                identify_hasher(usuario.contrasena)
                omitidas += 1
                continue
            except ValueError:
                pass

            usuario.contrasena = make_password(usuario.contrasena)
            usuario.save(update_fields=['contrasena'])
            cifradas += 1

        self.stdout.write(self.style.SUCCESS(
            f"✓ {cifradas} contraseña(s) cifrada(s); {omitidas} ya estaban cifradas."
        ))