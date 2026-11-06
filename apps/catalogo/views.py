from functools import wraps
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.utils.http import urlencode
from django.views.decorators.http import require_POST

from .models import Paquete, CategoriaDestino, Itinerario, Resena
from .forms import PaqueteForm, ItinerarioForm
from apps.pedidos.models import Reserva
from apps.usuarios.models import Usuario

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
    resenas = paquete.resenas.select_related('usuario')
    promedio = resenas.aggregate(p=Avg('calificacion'))['p']
    return render(request, 'catalogo/paquete_detalle.html', {
        'paquete': paquete,
        'relacionadas': relacionadas,
        'es_admin': es_administrador(request),
        'resenas': resenas,
        'promedio': promedio,
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

@admin_requerido
def gestion_itinerario(request):
    query = request.GET.get('q', '').strip()
    itinerarios = Itinerario.objects.all().select_related('paquete')
    
    if query:
        itinerarios = itinerarios.filter(
            Q(actividad__icontains=query) |
            Q(paquete__nombre__icontains=query)
        )
        
    paginador = Paginator(itinerarios.order_by('paquete__nombre', 'dia', 'horario'), 10)
    pagina = paginador.get_page(request.GET.get('page'))
    
    return render(request, 'catalogo/gestion_itinerario.html', {'itinerarios': pagina, 'query': query})

@admin_requerido
def itinerario_crear(request):
    if request.method == 'POST':
        form = ItinerarioForm(request.POST)
        if form.is_valid():
            itinerario = form.save()
            messages.success(request, f"Actividad '{itinerario.actividad}' agregada exitosamente.")
            return redirect('catalogo:gestion_itinerario')
    else:
        form = ItinerarioForm()
        
    return render(request, 'catalogo/itinerario_form.html', {
        'form': form,
        'titulo_accion': 'Agregar Actividad al Itinerario',
        'boton_texto': 'Guardar Actividad',
    })

@admin_requerido
def itinerario_editar(request, id):
    itinerario = get_object_or_404(Itinerario, id=id)
    if request.method == 'POST':
        form = ItinerarioForm(request.POST, instance=itinerario)
        if form.is_valid():
            form.save()
            messages.success(request, f"Actividad '{itinerario.actividad}' actualizada.")
            return redirect('catalogo:gestion_itinerario')
    else:
        form = ItinerarioForm(instance=itinerario)
        
    return render(request, 'catalogo/itinerario_form.html', {
        'form': form,
        'itinerario': itinerario,
        'titulo_accion': 'Editar Actividad del Itinerario',
        'boton_texto': 'Actualizar Actividad',
    })

@admin_requerido
def itinerario_eliminar(request, id):
    itinerario = get_object_or_404(Itinerario, id=id)
    if request.method == 'POST':
        actividad = itinerario.actividad
        itinerario.delete()
        messages.success(request, f"Actividad '{actividad}' eliminada del itinerario.")
        return redirect('catalogo:gestion_itinerario')
        
    return render(request, 'catalogo/itinerario_confirmar_eliminar.html', {'itinerario': itinerario})

@require_POST
def guardar_resena(request, id):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.filter(pk=usuario_id).first() if usuario_id else None
    if not usuario:
        messages.warning(request, "Debes iniciar sesión para dejar una reseña.")
        return redirect(f"/usuarios/login/?{urlencode({'next': request.get_full_path()})}")

    paquete = get_object_or_404(Paquete, pk=id)

    es_pasajero = Reserva.objects.filter(
        usuario=usuario,
        paquete=paquete,
        estado='Pagada',
    ).exists()
    if not es_pasajero:
        messages.error(request, "Solo puedes reseñar paquetes que hayas pagado.")
        return redirect('usuarios:perfil')

    try:
        calificacion = int(request.POST.get('calificacion', 0))
    except ValueError:
        calificacion = 0
    comentario = request.POST.get('comentario', '').strip()

    if calificacion not in range(1, 6) or not comentario:
        messages.error(request, "Debes elegir una calificación y escribir un comentario.")
        return redirect('usuarios:perfil')

    Resena.objects.update_or_create(
        usuario=usuario,
        paquete=paquete,
        defaults={'calificacion': calificacion, 'comentario': comentario},
    )
    messages.success(request, "¡Gracias por tu reseña!")
    return redirect('usuarios:perfil')