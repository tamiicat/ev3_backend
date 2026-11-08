from django.contrib import admin
from .models import Hotel, Vuelo, Paquete, Itinerario, Resena

# personalización del panel de administración
admin.site.site_header = "Agencia de Viajes - Panel de Administración"   # barra superior
admin.site.site_title = "Admin Viajes"                                   # título de la pestaña
admin.site.index_title = "Gestión de Catálogo y Reservas"                # título de la portada

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ciudad', 'categoria', 'habitacion', 'servicios')
    list_filter = ('ciudad', 'categoria', 'servicios')
    search_fields = ('nombre', 'ciudad', 'direccion')
    list_editable = ('servicios', 'categoria')
    list_per_page = 15

@admin.register(Vuelo)
class VueloAdmin(admin.ModelAdmin):
    list_display = ('aerolinea', 'ciudad_origen', 'ciudad_destino', 'fecha_salida', 'hora_salida', 'fecha_llegada')
    list_filter = ('aerolinea', 'ciudad_origen', 'ciudad_destino')
    search_fields = ('aerolinea', 'ciudad_origen', 'ciudad_destino')
    list_per_page = 15

@admin.register(Paquete)
class PaqueteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'precio_paquete', 'cupos_disponibles', 'fecha_inicio')
    list_filter = ('categoria', 'fecha_inicio', 'fecha_fin')
    search_fields = ('id', 'nombre', 'descripcion')
    list_editable = ('precio_paquete', 'cupos_disponibles')

    fieldsets = (
        ('Información Principal', {
            'fields': ('nombre', 'categoria', 'descripcion')
        }),
        ('Valores y Disponibilidad', {
            'fields': ('precio_paquete', 'cupos_disponibles')
        }),
        ('Vigencia del Viaje', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Servicios Incluidos (Relaciones)', {
            'fields': ('hoteles', 'vuelos'),
            'classes': ('collapse',)
        }),
    )
    # reemplaza el <select multiple> por un selector de dos columnas (disponibles / elegidos)
    filter_horizontal = ('hoteles', 'vuelos')
    list_per_page = 15

@admin.register(Itinerario)
class ItinerarioAdmin(admin.ModelAdmin):
    list_display = ('paquete', 'dia', 'actividad', 'horario')
    list_filter = ('paquete', 'dia')
    search_fields = ('actividad', 'descripcion', 'paquete__nombre')
    list_per_page = 20

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'paquete', 'calificacion', 'fecha_publicacion')
    list_filter = ('calificacion', 'fecha_publicacion')
    search_fields = ('usuario__nombre', 'usuario__apellido', 'paquete__nombre', 'comentario')
    list_per_page = 20