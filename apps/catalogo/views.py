from functools import wraps
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.utils.http import urlencode
from django.views.decorators.http import require_POST

from .models import Paquete, CategoriaDestino, Itinerario, Resena, Hotel, Vuelo
from .forms import PaqueteForm, ItinerarioForm, HotelForm, VueloForm
from apps.pedidos.models import Reserva
from apps.usuarios.models import Usuario

# CONTROL DE ACCESO
def es_administrador(request):
    # el proyecto maneja DOS mecanismos de autenticación:
    # a) sesión propia: al iniciar sesión, el login guarda en request.session
    # b) autenticación estándar de Django (request.user): staff o superusuario.

    if request.session.get('usuario_rol') == 'administrador':
        return True
    # getattr evita errores si por alguna razón el request no tiene atributo "user".
    user = getattr(request, 'user', None)
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))

def admin_requerido(view_func):
    # decorador que protege una vista: solo deja pasar a administradores.
    @wraps(view_func)  # conserva el nombre y la documentación de la vista original
    def wrapper(request, *args, **kwargs):
        if not (request.session.get('usuario_id') or request.user.is_authenticated):
            messages.warning(request, "Debes iniciar sesión para acceder a esta página.")
            # urlencode codifica la URL actual para pasarla de forma segura como parámetro.
            return redirect(f"/usuarios/login/?{urlencode({'next': request.get_full_path()})}")
        if not es_administrador(request):
            messages.error(request, "No tienes permisos de administrador para acceder a esta sección.")
            return redirect('catalogo:lista')
        return view_func(request, *args, **kwargs)
    return wrapper

# PARTE PÚBLICA: LISTADO Y DETALLE
def paquete_lista(request):
    # catálogo público: búsqueda por texto, filtro por continente, orden y paginación."""
    query = request.GET.get('q', '').strip()
    categoria_slug = request.GET.get('categoria', '')
    orden = request.GET.get('orden', '-fecha_inicio')
    paquetes = Paquete.objects.filter(activo=True).select_related('categoria')

    # filtro por continente usando el slug de la categoría.
    if categoria_slug:
        paquetes = paquetes.filter(categoria__slug=categoria_slug)

    # búsqueda de texto: Q permite combinar condiciones con OR (|).
    if query:
        paquetes = paquetes.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query)
        )

    # lista blanca de órdenes permitidos: el valor recibido por URL se traduce a un
    # campo real. Si llega algo no esperado, .get() usa '-fecha_inicio' por defecto,
    # evitando ordenar por campos arbitrarios enviados por el usuario.
    ordenes_validos = {
        'precio_asc': 'precio_paquete',
        'precio_desc': '-precio_paquete',
        'nombre_asc': 'nombre',
        'recientes': '-fecha_inicio',
    }
    paquetes = paquetes.order_by(ordenes_validos.get(orden, '-fecha_inicio'))

    # paginación: 6 paquetes por página. get_page tolera páginas inválidas
    paginador = Paginator(paquetes, 6)
    pagina = paginador.get_page(request.GET.get('page'))
    categorias = CategoriaDestino.objects.all()  # para armar el filtro de continentes

    # el diccionario son las variables disponibles en la plantilla.
    return render(request, 'catalogo/paquete_lista.html', {
        'paquetes': pagina,
        'categorias': categorias,
        'categoria_seleccionada': categoria_slug,
        'query_actual': query,
        'orden_actual': orden,
        'total_resultados': paquetes.count(),
    })

def paquete_detalle(request, id):
    # detalle de un paquete (solo si está activo), con relacionados y reseñas
    paquete = get_object_or_404(Paquete.objects.select_related('categoria'), id=id, activo=True)
    relacionadas = Paquete.objects.filter(categoria=paquete.categoria, activo=True).exclude(pk=paquete.pk)[:3]
    # reseñas del paquete (con el usuario precargado) y su calificación promedio.
    resenas = paquete.resenas.select_related('usuario')
    promedio = resenas.aggregate(p=Avg('calificacion'))['p']

    return render(request, 'catalogo/paquete_detalle.html', {
        'paquete': paquete,
        'relacionadas': relacionadas,
        'es_admin': es_administrador(request),  # la plantilla puede mostrar botones de edición
        'resenas': resenas,
        'promedio': promedio,
    })

# CRUD DE PAQUETES (solo administradores)
@admin_requerido
def gestion_paquetes(request):
    # tabla de administración de paquetes (incluye los inactivos) con buscador.
    query = request.GET.get('q', '').strip()
    paquetes = Paquete.objects.all().select_related('categoria')
    if query:
        paquetes = paquetes.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query)
        )
    paginador = Paginator(paquetes.order_by('-fecha_inicio'), 10)  # 10 por página
    pagina = paginador.get_page(request.GET.get('page'))
    return render(request, 'catalogo/gestion_paquete.html', {'paquetes': pagina, 'query': query})

@admin_requerido
def paquete_crear(request):
    # crea un paquete nuevo
    if request.method == 'POST':
        # request.FILES es necesario para recibir la imagen subida.
        form = PaqueteForm(request.POST, request.FILES)
        if form.is_valid():
            paquete = form.save()
            messages.success(request, f"¡Paquete '{paquete.nombre}' creado exitosamente!")
            return redirect('catalogo:gestion')
    else:
        form = PaqueteForm()  # GET: formulario vacío
    # si el POST no fue válido se llega aquí con el form con errores y se vuelve a mostrar.
    return render(request, 'catalogo/nomade_form.html', {
        'form': form,
        'titulo_accion': 'Ingresar Nuevo Paquete',
        'boton_texto': 'Guardar',
    })

@admin_requerido
def paquete_editar(request, id):
    # edita un paquete existente (misma plantilla que crear).
    paquete = get_object_or_404(Paquete, id=id)
    if request.method == 'POST':
        # instance=paquete indica que se ACTUALIZA ese registro en lugar de crear uno nuevo.
        form = PaqueteForm(request.POST, request.FILES, instance=paquete)
        if form.is_valid():
            form.save()
            messages.success(request, f"Paquete '{paquete.nombre}' actualizado.")
            return redirect('catalogo:gestion')
    else:
        form = PaqueteForm(instance=paquete)  # formulario precargado con los datos actuales
    return render(request, 'catalogo/nomade_form.html', {
        'form': form,
        'paquete': paquete,
        'titulo_accion': 'Editar Paquete',
        'boton_texto': 'Actualizar',
    })

@admin_requerido
def paquete_eliminar(request, id):
    # elimina un paquete. GET muestra una pantalla de confirmación; POST borra
    paquete = get_object_or_404(Paquete, id=id)
    if request.method == 'POST':
        nombre = paquete.nombre   # se guarda antes de borrar, para usarlo en el mensaje
        paquete.delete()          # borra también sus itinerarios y reseñas (CASCADE)
        messages.success(request, f"Paquete '{nombre}' eliminado.")
        return redirect('catalogo:gestion')
    return render(request, 'catalogo/nomade_confirmar_eliminar.html', {'paquete': paquete})

# CRUD DE ITINERARIOS (solo administradores)
@admin_requerido
def gestion_itinerario(request):
    # listado de actividades de itinerario, con buscador por actividad o por paquete.
    query = request.GET.get('q', '').strip()
    itinerarios = Itinerario.objects.all().select_related('paquete')

    if query:
        itinerarios = itinerarios.filter(
            Q(actividad__icontains=query) |
            Q(paquete__nombre__icontains=query)
        )

    # orden: por paquete, luego por fecha y hora (así el itinerario se lee cronológicamente).
    paginador = Paginator(itinerarios.order_by('paquete__nombre', 'dia', 'horario'), 10)
    pagina = paginador.get_page(request.GET.get('page'))

    return render(request, 'catalogo/gestion_itinerario.html', {'itinerarios': pagina, 'query': query})

@admin_requerido
def itinerario_crear(request):
    # crea una actividad nueva para el itinerario
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
    # edita una actividad existente
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
    # elimina una actividad (confirmación por GET, borrado por POST)
    itinerario = get_object_or_404(Itinerario, id=id)
    if request.method == 'POST':
        actividad = itinerario.actividad
        itinerario.delete()
        messages.success(request, f"Actividad '{actividad}' eliminada del itinerario.")
        return redirect('catalogo:gestion_itinerario')

    return render(request, 'catalogo/itinerario_confirmar_eliminar.html', {'itinerario': itinerario})

# RESEÑAS (usuarios con sesión que pagaron el paquete)
@require_POST 
def guardar_resena(request, id):
    # Guarda (o actualiza) la reseña de un usuario sobre un paquete.
    # identificar al usuario a partir de la sesión.
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.filter(pk=usuario_id).first() if usuario_id else None
    if not usuario:
        messages.warning(request, "Debes iniciar sesión para dejar una reseña.")
        return redirect(f"/usuarios/login/?{urlencode({'next': request.get_full_path()})}")

    paquete = get_object_or_404(Paquete, pk=id)

    # verificar que exista una reserva pagada de este usuario para este paquete.
    es_pasajero = Reserva.objects.filter(
        usuario=usuario,
        paquete=paquete,
        estado='Pagada',
    ).exists()
    if not es_pasajero:
        messages.error(request, "Solo puedes reseñar paquetes que hayas pagado.")
        return redirect('usuarios:perfil')

    # validar los datos del formulario. Si la calificación no es un número,
    try:
        calificacion = int(request.POST.get('calificacion', 0))
    except ValueError:
        calificacion = 0
    comentario = request.POST.get('comentario', '').strip()

    if calificacion not in range(1, 6) or not comentario:
        messages.error(request, "Debes elegir una calificación y escribir un comentario.")
        return redirect('usuarios:perfil')

    # update_or_create: si ya existe una reseña de este usuario para este paquete la actualiza; si no, la crea. Coincide con unique_together = ('usuario', 'paquete').
    Resena.objects.update_or_create(
        usuario=usuario,
        paquete=paquete,
        defaults={'calificacion': calificacion, 'comentario': comentario},
    )
    messages.success(request, "¡Gracias por tu reseña!")
    return redirect('usuarios:perfil')

# CRUD DE HOTELES (solo administradores)
@admin_requerido
def gestion_hotel(request):
    # listado de hoteles
    query = request.GET.get('q', '').strip()
    hoteles = Hotel.objects.all().prefetch_related('paquetes')

    if query:
        hoteles = hoteles.filter(
            Q(nombre__icontains=query) |
            Q(ciudad__icontains=query) |
            Q(paquetes__nombre__icontains=query)
        ).distinct()  # distinct(): buscar por paquetes hace un JOIN que puede repetir hoteles

    paginador = Paginator(hoteles.order_by('nombre'), 10)
    pagina = paginador.get_page(request.GET.get('page'))

    return render(request, 'catalogo/gestion_hotel.html', {'hoteles': pagina, 'query': query})

@admin_requerido
def hotel_crear(request):
    # creación de un hotel (y lo asocia a los paquetes elegidos en el formulario)
    if request.method == 'POST':
        form = HotelForm(request.POST)
        if form.is_valid():
            hotel = form.save()   # HotelForm.save() también sincroniza la relación con paquetes
            messages.success(request, f"Hotel '{hotel.nombre}' agregado exitosamente.")
            return redirect('catalogo:gestion_hotel')
    else:
        form = HotelForm()

    return render(request, 'catalogo/hotel_form.html', {
        'form': form,
        'titulo_accion': 'Agregar Hotel',
        'boton_texto': 'Guardar Hotel',
    })

@admin_requerido
def hotel_editar(request, id):
    # edita un hotel y los paquetes en los que se incluye
    hotel = get_object_or_404(Hotel, id=id)
    if request.method == 'POST':
        form = HotelForm(request.POST, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, f"Hotel '{hotel.nombre}' actualizado.")
            return redirect('catalogo:gestion_hotel')
    else:
        form = HotelForm(instance=hotel)

    return render(request, 'catalogo/hotel_form.html', {
        'form': form,
        'hotel': hotel,
        'titulo_accion': 'Editar Hotel',
        'boton_texto': 'Actualizar Hotel',
    })

@admin_requerido
def hotel_eliminar(request, id):
    # elimina un hotel. La pantalla de confirmación muestra los paquetes afectados
    hotel = get_object_or_404(Hotel, id=id)
    if request.method == 'POST':
        nombre = hotel.nombre
        hotel.delete()   # solo elimina el hotel y sus vínculos; los paquetes NO se borran
        messages.success(request, f"Hotel '{nombre}' eliminado.")
        return redirect('catalogo:gestion_hotel')

    return render(request, 'catalogo/hotel_confirmar_eliminar.html', {
        'hotel': hotel,
        'paquetes_asociados': hotel.paquetes.all(),
    })

# CRUD DE VUELOS (solo administradores)
@admin_requerido
def gestion_vuelo(request):
    # listado de vuelos con buscador por aerolínea, origen, destino o paquete
    query = request.GET.get('q', '').strip()
    vuelos = Vuelo.objects.all().prefetch_related('paquetes')

    if query:
        vuelos = vuelos.filter(
            Q(aerolinea__icontains=query) |
            Q(ciudad_origen__icontains=query) |
            Q(ciudad_destino__icontains=query) |
            Q(paquetes__nombre__icontains=query)
        ).distinct()

    # orden cronológico de salida.
    paginador = Paginator(vuelos.order_by('fecha_salida', 'hora_salida'), 10)
    pagina = paginador.get_page(request.GET.get('page'))

    return render(request, 'catalogo/gestion_vuelo.html', {'vuelos': pagina, 'query': query})

@admin_requerido
def vuelo_crear(request):
    # crea un vuelo (y lo asocia a los paquetes elegidos)
    if request.method == 'POST':
        form = VueloForm(request.POST)
        if form.is_valid():
            vuelo = form.save()
            messages.success(request, f"Vuelo '{vuelo}' agregado exitosamente.")
            return redirect('catalogo:gestion_vuelo')
    else:
        form = VueloForm()

    return render(request, 'catalogo/vuelo_form.html', {
        'form': form,
        'titulo_accion': 'Agregar Vuelo',
        'boton_texto': 'Guardar Vuelo',
    })

@admin_requerido
def vuelo_editar(request, id):
    # edita un vuelo y los paquetes en los que se incluye
    vuelo = get_object_or_404(Vuelo, id=id)
    if request.method == 'POST':
        form = VueloForm(request.POST, instance=vuelo)
        if form.is_valid():
            form.save()
            messages.success(request, f"Vuelo '{vuelo}' actualizado.")
            return redirect('catalogo:gestion_vuelo')
    else:
        form = VueloForm(instance=vuelo)

    return render(request, 'catalogo/vuelo_form.html', {
        'form': form,
        'vuelo': vuelo,
        'titulo_accion': 'Editar Vuelo',
        'boton_texto': 'Actualizar Vuelo',
    })

@admin_requerido
def vuelo_eliminar(request, id):
    # elimina un vuelo (confirmación por GET, borrado por POST)
    vuelo = get_object_or_404(Vuelo, id=id)
    if request.method == 'POST':
        descripcion = str(vuelo)   # se guarda la descripción antes de borrar, para el mensaje
        vuelo.delete()
        messages.success(request, f"Vuelo '{descripcion}' eliminado.")
        return redirect('catalogo:gestion_vuelo')

    return render(request, 'catalogo/vuelo_confirmar_eliminar.html', {
        'vuelo': vuelo,
        'paquetes_asociados': vuelo.paquetes.all(),
    })