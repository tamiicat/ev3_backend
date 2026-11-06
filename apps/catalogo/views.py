from functools import wraps
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.http import urlencode

from .models import Paquete, CategoriaDestino
from .forms import PaqueteForm

def es_administrador(request):
    if request.session.get('usuario_rol') == 'administrador':
        return True
    user = getattr(request, 'user', None)
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))

def admin_requerido(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not (request.session.get('usuario_id') or request.user.is_authenticated):
            messages.warning(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect(f"/usuarios/login/?{urlencode({'next': request.get_full_path()})}")
        if not es_administrador(request):
            messages.error(request, "No tienes permisos de administrador para acceder a esta sección.")
            return redirect('catalogo:lista')
        return view_func(request, *args, **kwargs)
    return wrapper

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
    categorias = CategoriaDestino.objects.all()

    return render(request, 'catalogo/paquete_lista.html', {
        'paquetes': pagina,
        'categorias': categorias,
        'categoria_seleccionada': categoria_slug,
        'query_actual': query,
        'orden_actual': orden,
        'total_resultados': paquetes.count(),
    })

def paquete_detalle(request, id):
        paquete = get_object_or_404(Paquete.objects.select_related('categoria'), id=id, activo=True)
        relacionadas = Paquete.objects.filter(categoria=paquete.categoria, activo=True).exclude(pk=paquete.pk)[:3]
        return render(request, 'catalogo/paquete_detalle.html', {
            'paquete': paquete,
            'relacionadas': relacionadas,
            'es_admin': es_administrador(request),
        })
        
@admin_requerido
def gestion_paquetes(request):
    query = request.GET.get('q', '').strip()
    paquetes = Paquete.objects.all().select_related('categoria')
    if query:
        paquetes = paquetes.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query)
        )
    paginador = Paginator(paquetes.order_by('-fecha_inicio'), 10)
    pagina = paginador.get_page(request.GET.get('page'))
    return render(request, 'catalogo/gestion_paquete.html', {'paquetes': pagina, 'query': query})

@admin_requerido
def paquete_crear(request):
    if request.method == 'POST':
        form = PaqueteForm(request.POST, request.FILES)
        if form.is_valid():
            paquete = form.save()
            messages.success(request, f"¡Paquete '{paquete.nombre}' creado exitosamente!")
            return redirect('catalogo:gestion')
    else:
        form = PaqueteForm()
    return render(request, 'catalogo/nomade_form.html', {
        'form': form,
        'titulo_accion': 'Ingresar Nuevo Paquete',
        'boton_texto': 'Guardar',
    })

@admin_requerido
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
    return render(request, 'catalogo/nomade_form.html', {
        'form': form,
        'paquete': paquete,
        'titulo_accion': 'Editar Paquete',
        'boton_texto': 'Actualizar',
    })

@admin_requerido
def paquete_eliminar(request, id):
    paquete = get_object_or_404(Paquete, id=id)
    if request.method == 'POST':
        nombre = paquete.nombre
        paquete.delete()
        messages.success(request, f"Paquete '{nombre}' eliminado.")
        return redirect('catalogo:gestion')
    return render(request, 'catalogo/nomade_confirmar_eliminar.html', {'paquete': paquete})