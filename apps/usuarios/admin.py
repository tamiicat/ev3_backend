from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre', 'apellido', 'correo_electronico', 'telefono', 'rol')
    list_filter = ('rol',)
    search_fields = ('rut', 'nombre', 'apellido', 'correo_electronico')
    list_editable = ('rol',)   # el rol se puede cambiar directamente desde el listado
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        if not change or 'contrasena' in form.changed_data:
            obj.set_password(obj.contrasena)
        super().save_model(request, obj, form, change)