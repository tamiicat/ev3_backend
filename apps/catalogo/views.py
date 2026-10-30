from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Paquete, Categoria
from .forms import PaqueteForm

def es_administrador(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def paquete_lista(request):
    query = request.GET.get('q', '').strip()
    categoria_slug = request.GET.get('categoria', '')
    orden = request.GET.get('orden', '-fecha_inicio')

    paquetes = Paquete.objects.filter(activo=True).select_related('categoria')

    if categoria_slug:
        paquetes = paquetes.filter(categoria__slug=categoria_slug)

    if query:
        paquetes = paquetes.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query)
        )

    ordenes_validos = {
        'precio_asc': 'precio_paquete',
        'precio_desc': '-precio_paquete',
        'nombre_asc': 'nombre',
        'recientes': '-fecha_inicio',
    }
    paquetes = paquetes.order_by(ordenes_validos.get(orden, '-fecha_inicio'))

    paginador = Paginator(paquetes, 6)
    pagina = paginador.get_page(request.GET.get('page'))
    categorias = Categoria.objects.filter(activo=True)

    return render(request, 'catalogo/paquete_lista.html', {
        'paquetes': pagina,
        'categorias': categorias,
        'categoria_seleccionada': categoria_slug,
        'query_actual': query,
        'orden_actual': orden,
        'total_resultados': paquetes.count(),
    })

def paquete_detalle(request, slug):
    paquete = get_object_or_404(Paquete.objects.select_related('categoria'), slug=slug, activo=True)
    relacionadas = Paquete.objects.filter(categoria=paquete.categoria, activo=True).exclude(pk=paquete.pk)[:3]
    return render(request, 'catalogo/paquete_detalle.html', {'paquete': paquete, 'relacionadas': relacionadas})

@login_required
@user_passes_test(es_administrador, login_url='catalogo:lista')
def gestion_paquetes(request):
    query = request.GET.get('q', '').strip()
    paquetes = Paquete.objects.all().select_related('categoria')
    if query:
        paquetes = paquetes.filter(Q(nombre__icontains=query))
    paginador = Paginator(paquetes.order_by('-fecha_inicio'), 10)
    pagina = paginador.get_page(request.GET.get('page'))
    return render(request, 'catalogo/gestion_paquetes.html', {'paquetes': pagina, 'query': query})

@login_required
@user_passes_test(es_administrador, login_url='catalogo:lista')
def paquete_crear(request):
    if request.method == 'POST':
        form = PaqueteForm(request.POST, request.FILES)
        if form.is_valid():
            paquete = form.save()
            messages.success(request, f"¡Paquete '{paquete.nombre}' creado exitosamente!")
            return redirect('catalogo:gestion')
    else:
        form = PaqueteForm()
    return render(request, 'catalogo/paquete_form.html', {'form': form, 'titulo_accion': 'Ingresar Nuevo Paquete', 'boton_texto': 'Guardar'})

@login_required
@user_passes_test(es_administrador, login_url='catalogo:lista')
def paquete_editar(request, id):
    paquete = get_object_or_404(Paquete, id=id)
    if request.method == 'POST':
        form = PaqueteForm(request.POST, request.FILES, instance=paquete)
        if form.is_valid():
            form.save()
            messages.success(request, f"Paquete '{paquete.nombre}' actualizado.")
            return redirect('catalogo:gestion')
    else:
        form = PaqueteForm(instance=paquete)
    return render(request, 'catalogo/paquete_form.html', {'form': form, 'paquete': paquete, 'titulo_accion': 'Editar Paquete', 'boton_texto': 'Actualizar'})

@login_required
@user_passes_test(es_administrador, login_url='catalogo:lista')
def paquete_eliminar(request, id):
    paquete = get_object_or_404(Paquete, id=id)
    if request.method == 'POST':
        nombre = paquete.nombre
        paquete.delete()
        messages.success(request, f"Paquete '{nombre}' eliminado.")
        return redirect('catalogo:gestion')
    return render(request, 'catalogo/paquete_confirmar_eliminar.html', {'paquete': paquete})