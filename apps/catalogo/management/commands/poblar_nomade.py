from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from catalogo.models import Paquete, Hotel, Vuelo, Itinerario
from usuarios.models import Usuario

class Command(BaseCommand):
    help = "Puebla la base de datos con paquetes turísticos, hoteles, vuelos e itinerarios para la agencia Nomade, respetando el Modelo Relacional."

    def handle(self, *args, **kwargs):
        # Creación de Superusuario panel administrador
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@nomade.cl", "admin")
            self.stdout.write(self.style.SUCCESS("✓ Superusuario nativo 'admin' creado."))

        # Creación de Usuario Administrador
        if not Usuario.objects.filter(correo_electronico="admin@nomade.cl").exists():
            Usuario.objects.create(
                rut="12345678-9",
                nombre="Administrador",
                apellido="Nomade",
                telefono=987654321,
                correo_electronico="admin@nomade.cl",
                contrasena="admin",
                rol="administrador"
            )
            self.stdout.write(self.style.SUCCESS("✓ Usuario administrador de agencia creado."))

        # Servicios (Hoteles y Vuelos)
        hotel_rio, _ = Hotel.objects.get_or_create(
            nombre="Copacabana Palace", 
            defaults={'ciudad': "Río de Janeiro", 'direccion': "Av. Atlántica 1702", 'categoria': "5 Estrellas", 'habitacion': 101, 'servicios': True}
        )
        hotel_cusco, _ = Hotel.objects.get_or_create(
            nombre="Inca Imperial", 
            defaults={'ciudad': "Cusco", 'direccion': "Calle Ruinas 465", 'categoria': "3 Estrellas", 'habitacion': 205, 'servicios': True}
        )

        vuelo_rio, _ = Vuelo.objects.get_or_create(
            aerolinea="LATAM", ciudad_origen="Santiago", ciudad_destino="Río de Janeiro", 
            defaults={'fecha_salida': '2027-01-15', 'hora_salida': '08:00', 'fecha_llegada': '2027-01-15', 'hora_llegada': '12:30'}
        )
        vuelo_cusco, _ = Vuelo.objects.get_or_create(
            aerolinea="Sky Airlines", ciudad_origen="Santiago", ciudad_destino="Cusco", 
            defaults={'fecha_salida': '2027-02-10', 'hora_salida': '09:00', 'fecha_llegada': '2027-02-10', 'hora_llegada': '11:00'}
        )

        # Paquetes Turísticos
        paquete_rio, created_rio = Paquete.objects.get_or_create(
            nombre="Verano en Río de Janeiro",
            defaults={
                'descripcion': "Disfruta de las playas más famosas de Brasil con caipirinhas incluidas.",
                'precio_paquete': 450000.0,
                'cupos_disponibles': 20,
                'fecha_inicio': '2027-01-15',
                'fecha_fin': '2027-01-22',
            }
        )
        if created_rio:
            paquete_rio.hoteles.add(hotel_rio)
            paquete_rio.vuelos.add(vuelo_rio)
            Itinerario.objects.get_or_create(paquete=paquete_rio, dia='2027-01-16', defaults={'actividad': "City Tour Río", 'descripcion': "Visita al Cristo Redentor.", 'horario': '09:00'})

        paquete_cusco, created_cusco = Paquete.objects.get_or_create(
            nombre="Ruta del Imperio Inca",
            defaults={
                'descripcion': "Expedición por Cusco, Valle Sagrado y Machu Picchu.",
                'precio_paquete': 320000.0,
                'cupos_disponibles': 15,
                'fecha_inicio': '2027-02-10',
                'fecha_fin': '2027-02-17',
            }
        )
        if created_cusco:
            paquete_cusco.hoteles.add(hotel_cusco)
            paquete_cusco.vuelos.add(vuelo_cusco)
            Itinerario.objects.get_or_create(paquete=paquete_cusco, dia='2027-02-11', defaults={'actividad': "Tour Ciudad de Cusco", 'descripcion': "Visita a plazas y ruinas.", 'horario': '10:00'})

        self.stdout.write(self.style.SUCCESS("✓ Catálogo de Nomade poblado exitosamente con paquetes, hoteles, vuelos e itinerarios."))