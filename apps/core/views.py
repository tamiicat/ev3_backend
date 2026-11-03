from django.shortcuts import render
from apps.catalogo.models import Paquete

def inicio(request):

    paquetes_destacados = Paquete.objects.all().order_by('fecha_inicio')[:4]

    return render(request, 'core/index.html', {
        'paquetes_destacados': paquetes_destacados,
        'total_paquetes': Paquete.objects.count(),
    })

def nosotros(request):
    return render(request, 'core/nosotros.html')