from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre', 'apellido', 'correo_electronico', 'telefono', 'rol')
    list_filter = ('rol',)
    search_fields = ('rut', 'nombre', 'apellido', 'correo_electronico')
    list_editable = ('rol',)
    list_per_page = 20