import io
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.catalogo.models import Paquete, Hotel, Vuelo, Itinerario, CategoriaDestino
from apps.usuarios.models import Usuario

# CREACIÓN DE PAQUETES TURÍSTICOS
PAQUETES = [
    {
        "nombre": "Verano en Río de Janeiro",
        "continente": "América del Sur",   
        "descripcion": "Disfruta de las playas más famosas de Brasil con caipirinhas incluidas.",
        "precio": 450000.0,
        "cupos": 20,
        "inicio": "2027-01-15",
        "fin": "2027-01-22",
        "color": (255, 140, 0),
        "hoteles": [
            {"nombre": "Copacabana Palace", "ciudad": "Río de Janeiro", "direccion": "Av. Atlántica 1702", "categoria": "5 Estrellas", "habitacion": 101},
            {"nombre": "Fasano Rio de Janeiro", "ciudad": "Río de Janeiro", "direccion": "Av. Vieira Souto 80", "categoria": "5 Estrellas", "habitacion": 312},
        ],
        "destino_vuelo": "Río de Janeiro",
        "vuelos": [
            ("LATAM", 0, "08:00", "12:30", 0),
            ("Sky Airlines", 0, "14:00", "18:45", 0),
            ("LATAM", 1, "07:30", "12:00", 0),
            ("Gol", 1, "16:00", "20:40", 0),
        ],
        "itinerario": [
            ("Llegada y check-in", "Recepción en el aeropuerto, traslado al hotel y tarde libre en Copacabana.", "15:00"),
            ("City Tour Río", "Visita al Cristo Redentor y al barrio de Santa Teresa.", "09:00"),
            ("Pão de Açúcar", "Ascenso en teleférico al atardecer con vista a la bahía de Guanabara.", "16:00"),
            ("Playas de Ipanema y Leblon", "Día de playa con almuerzo de mariscos frente al mar.", "10:00"),
            ("Bosque de Tijuca y Jardín Botánico", "Caminata guiada por la selva urbana más grande del mundo.", "09:30"),
            ("Noche de samba en Lapa", "Cena y show de samba en vivo en el barrio bohemio de Lapa.", "20:00"),
            ("Mañana libre y regreso", "Tiempo libre para compras y traslado al aeropuerto.", "11:00"),
        ],
    },
    {
        "nombre": "Ruta del Imperio Inca",
        "continente": "América del Sur",
        "descripcion": "Expedición por Cusco, Valle Sagrado y Machu Picchu.",
        "precio": 320000.0,
        "cupos": 15,
        "inicio": "2027-02-10",
        "fin": "2027-02-17",
        "color": (139, 90, 43),
        "hoteles": [
            {"nombre": "Inca Imperial", "ciudad": "Cusco", "direccion": "Calle Ruinas 465", "categoria": "3 Estrellas", "habitacion": 205},
            {"nombre": "Casa Andina Premium Cusco", "ciudad": "Cusco", "direccion": "Plaza Nazarenas 211", "categoria": "5 Estrellas", "habitacion": 118},
        ],
        "destino_vuelo": "Cusco",
        "vuelos": [
            ("Sky Airlines", 0, "09:00", "11:00", 0),
            ("LATAM", 0, "13:30", "15:45", 0),
            ("JetSMART", 1, "06:45", "08:50", 0),
            ("LATAM", 1, "18:00", "20:10", 0),
        ],
        "itinerario": [
            ("Llegada y aclimatación", "Traslado al hotel y descanso para adaptarse a la altura.", "13:00"),
            ("Tour Ciudad de Cusco", "Visita a plazas, la Catedral y las ruinas de Sacsayhuamán.", "10:00"),
            ("Valle Sagrado: Pisac", "Recorrido por el mercado artesanal y el complejo arqueológico de Pisac.", "08:30"),
            ("Valle Sagrado: Ollantaytambo", "Visita a la fortaleza inca y almuerzo típico andino.", "10:00"),
            ("Tren a Machu Picchu", "Viaje en tren panorámico hasta Aguas Calientes y noche en el pueblo.", "07:00"),
            ("Ciudadela de Machu Picchu", "Visita guiada a la ciudadela y regreso a Cusco.", "06:00"),
            ("Montaña de Colores / Día libre", "Excursión opcional o tiempo libre, y traslado final al aeropuerto.", "09:00"),
        ],
    },
    {
        "nombre": "Escapada Romántica a París",
        "continente": "Europa",
        "descripcion": "Siete días recorriendo la Ciudad Luz: arte, gastronomía y paseos por el Sena.",
        "precio": 1450000.0,
        "cupos": 12,
        "inicio": "2027-04-05",
        "fin": "2027-04-12",
        "color": (70, 90, 160),
        "hoteles": [
            {"nombre": "Hôtel Lutetia", "ciudad": "París", "direccion": "45 Boulevard Raspail", "categoria": "5 Estrellas", "habitacion": 402},
            {"nombre": "Hôtel Saint-Michel", "ciudad": "París", "direccion": "17 Rue Gay-Lussac", "categoria": "4 Estrellas", "habitacion": 215},
        ],
        "destino_vuelo": "París",
        "vuelos": [
            ("Air France", 0, "22:30", "15:30", 1),
            ("LATAM", 0, "23:45", "17:00", 1),
            ("Iberia", 1, "21:15", "16:20", 1),
            ("Air France", 1, "23:00", "16:10", 1),
        ],
        "itinerario": [
            ("Llegada y paseo por el Sena", "Traslado al hotel y paseo en barco por el Sena al atardecer.", "17:00"),
            ("Torre Eiffel y Trocadéro", "Subida a la Torre Eiffel y picnic en los jardines del Trocadéro.", "10:00"),
            ("Museo del Louvre", "Visita guiada a las obras maestras del Louvre.", "09:30"),
            ("Montmartre y Sacré-Cœur", "Caminata por el barrio de los artistas y cena en una brasserie.", "11:00"),
            ("Palacio de Versalles", "Excursión de día completo a los palacios y jardines de Versalles.", "08:30"),
            ("Barrio Latino y Notre-Dame", "Recorrido por la Île de la Cité, el Barrio Latino y degustación de quesos.", "10:30"),
            ("Compras y despedida", "Tiempo libre en Le Marais y traslado al aeropuerto.", "12:00"),
        ],
    },
    {
        "nombre": "Tokio Tradicional y Moderno",
        "continente": "Asia",
        "descripcion": "Un viaje entre templos milenarios, tecnología de vanguardia y la mejor cocina japonesa.",
        "precio": 1650000.0,
        "cupos": 10,
        "inicio": "2027-05-10",
        "fin": "2027-05-17",
        "color": (200, 40, 60),
        "hoteles": [
            {"nombre": "Park Hyatt Tokyo", "ciudad": "Tokio", "direccion": "3-7-1-2 Nishi-Shinjuku, Shinjuku", "categoria": "5 Estrellas", "habitacion": 501},
            {"nombre": "Hotel Gracery Shinjuku", "ciudad": "Tokio", "direccion": "1-19-1 Kabukicho, Shinjuku", "categoria": "4 Estrellas", "habitacion": 320},
        ],
        "destino_vuelo": "Tokio",
        "vuelos": [
            ("Japan Airlines", 0, "23:50", "06:30", 2),
            ("ANA", 0, "22:15", "05:10", 2),
            ("Air Canada", 1, "20:40", "07:00", 2),
            ("Qatar Airways", 1, "21:30", "09:15", 2),
        ],
        "itinerario": [
            ("Llegada y barrio de Shinjuku", "Traslado al hotel y primer paseo por las luces de Shinjuku.", "16:00"),
            ("Templo Senso-ji y Asakusa", "Visita al templo más antiguo de Tokio y compras en Nakamise.", "09:00"),
            ("Shibuya y Harajuku", "Cruce de Shibuya, santuario Meiji y cultura pop en Takeshita.", "10:00"),
            ("Mercado de Tsukiji y Ginza", "Desayuno de sushi en el mercado y paseo por Ginza.", "08:00"),
            ("Akihabara y tecnología", "Recorrido por la ciudad de la electrónica, anime y videojuegos.", "11:00"),
            ("Excursión al Monte Fuji", "Día completo en Hakone y vistas al Monte Fuji.", "07:30"),
            ("Ceremonia del té y despedida", "Ceremonia tradicional del té y traslado al aeropuerto.", "10:00"),
        ],
    },
]

class Command(BaseCommand):
    def asignar_imagen(self, paquete, nombre, color):
        if paquete.imagen:
            return

        carpeta = "paquetes"
        for ext in ("jpg", "jpeg", "png", "webp"):
            ruta = settings.MEDIA_ROOT / carpeta / f"{paquete.slug}.{ext}"
            if ruta.exists():
                paquete.imagen.name = f"{carpeta}/{paquete.slug}.{ext}"
                paquete.save()
                return

        from PIL import Image, ImageDraw

        ancho, alto = 1200, 800
        img = Image.new("RGB", (ancho, alto), color)   # lienzo del color base
        draw = ImageDraw.Draw(img)
        # degradado vertical: se dibuja una línea horizontal
        for y in range(alto):
            f = 1 - (y / alto) * 0.6
            draw.line([(0, y), (ancho, y)], fill=tuple(int(c * f) for c in color))
        draw.text((60, alto - 120), nombre, fill=(255, 255, 255))

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        paquete.imagen.save(f"{paquete.slug}.jpg", ContentFile(buffer.getvalue()), save=True)

    def handle(self, *args, **kwargs):
        # CREACIÓN DE ADMINISTRADOR
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@nomade.cl", "admin")
            
        if not Usuario.objects.filter(correo_electronico="admin@nomade.cl").exists():
            Usuario.objects.create(
                rut="12345678-9",
                nombre="Administrador",
                apellido="Nomade",
                telefono=987654321,
                correo_electronico="admin@nomade.cl",
                contrasena=make_password("admin"),
                rol="administrador",
            )
        # mensaje de creación exitosa de admin
        self.stdout.write(self.style.SUCCESS("✓ Usuario administrador creado"))

        # CATEGORÍAS - DESTINOS
        nombres_continentes = [
            "África", "América del Norte", "América del Sur", "Asia",
            "Centroamérica y Caribe", "Europa", "Oceanía", "Medio Oriente",
        ]

        categorias = {}
        for nombre in nombres_continentes:
            cat, _ = CategoriaDestino.objects.get_or_create(
                nombre=nombre,
                defaults={"slug": slugify(nombre)},
            )
            categorias[nombre] = cat

        # PAQUETES CON SUS HOTELES, VUELOS E ITINERARIO
        for datos in PAQUETES:
            paquete, creado = Paquete.objects.get_or_create(
                nombre=datos["nombre"],
                defaults={
                    "slug": slugify(datos["nombre"]),
                    "categoria": categorias[datos["continente"]],
                    "descripcion": datos["descripcion"],
                    "precio_paquete": datos["precio"],
                    "cupos_disponibles": datos["cupos"],
                    "fecha_inicio": datos["inicio"],
                    "fecha_fin": datos["fin"],
                },
            )

            self.asignar_imagen(paquete, datos["nombre"], datos["color"])

            # hoteles
            for h in datos["hoteles"]:
                hotel, _ = Hotel.objects.get_or_create(
                    nombre=h["nombre"],
                    defaults={
                        "ciudad": h["ciudad"],
                        "direccion": h["direccion"],
                        "categoria": h["categoria"],
                        "habitacion": h["habitacion"],
                        "servicios": True,
                    },
                )
                paquete.hoteles.add(hotel)

            # vuelos 
            fecha_base = date.fromisoformat(datos["inicio"])
            for aerolinea, desplaz, hora_sal, hora_lle, dias_lle in datos["vuelos"]:
                f_salida = fecha_base + timedelta(days=desplaz)
                f_llegada = f_salida + timedelta(days=dias_lle)
                vuelo, _ = Vuelo.objects.get_or_create(
                    aerolinea=aerolinea,
                    ciudad_origen="Santiago",
                    ciudad_destino=datos["destino_vuelo"],
                    fecha_salida=f_salida.isoformat(),
                    hora_salida=hora_sal,
                    defaults={
                        "fecha_llegada": f_llegada.isoformat(),
                        "hora_llegada": hora_lle,
                    },
                )
                paquete.vuelos.add(vuelo)

            # itinerario 
            for i, (actividad, descripcion, horario) in enumerate(datos["itinerario"]):
                dia = fecha_base + timedelta(days=i)   # día 1 = inicio, día 2 = inicio+1, ...
                Itinerario.objects.get_or_create(
                    paquete=paquete,
                    dia=dia.isoformat(),
                    actividad=actividad,
                    defaults={"descripcion": descripcion, "horario": horario},
                )

            estado = "creado" if creado else "ya existía (relaciones verificadas)"

        self.stdout.write(self.style.SUCCESS("✓ Base de datos poblada exitosamente"))