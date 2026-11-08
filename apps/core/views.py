from django.shortcuts import render
# se importa el modelo Paquete de la app "catalogo": core no tiene modelos propios
from apps.catalogo.models import Paquete

def inicio(request):
    # portada del sitio (ruta: '' dentro de la app core).
    paquetes_destacados = Paquete.objects.all().order_by('fecha_inicio')[:4]

    # render(request, plantilla, contexto)
    return render(request, 'core/index.html', {
        'paquetes_destacados': paquetes_destacados,
        # count() ejecuta un SELECT COUNT(*): cuenta en la BD sin cargar los objetos.
        'total_paquetes': Paquete.objects.count(),
    })

def nosotros(request):
    # página estática "Nosotros" (ruta: 'nosotros/').
    return render(request, 'core/nosotros.html')