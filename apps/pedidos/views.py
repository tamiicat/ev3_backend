from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.catalogo.models import Paquete
from apps.usuarios.models import Usuario
from apps.pedidos.models import Reserva, Pago
from apps.usuarios.views import login_requerido_custom 

# reglas de selección por paquete
MIN_ACTIVIDADES = 3
MAX_ACTIVIDADES = 5
MIN_HOTELES = 1
MAX_HOTELES = 1   
MIN_VUELOS = 1
MAX_VUELOS = 1   

def _obtener_carrito(request):
    # devuelve el carrito de la sesión; si no existe, lo crea vacío (setdefault)
    return request.session.setdefault('carrito', {})

def _validar_seleccion(datos, campo, opciones, min_deseado, maximo, etiqueta, singular=None):
    # valida lo que el cliente marcó en un campo (actividades, hoteles o vuelos).
    total = opciones.count()
    if total == 0:
        return [], None

    minimo = min(min_deseado, total)
    ids = {int(x) for x in datos.getlist(campo) if x.isdigit()}

    if not (minimo <= len(ids) <= maximo):
        if minimo == maximo == 1 and singular:
            return None, f"Elige 1 {singular}."
        return None, f"Elige entre {minimo} y {maximo} {etiqueta}."

    elegidos = list(opciones.filter(id__in=ids))
    if len(elegidos) != len(ids):
        return None, f"La selección de {etiqueta} no es válida."

    return elegidos, None

def carrito_ver(request):
    """Muestra el carrito con subtotal, IVA (19%) y total."""
    carrito = _obtener_carrito(request)
    subtotal = sum(item['subtotal'] for item in carrito.values())
    iva = int(subtotal * 0.19)
    total = subtotal + iva
    return render(request, 'pedidos/carrito.html', {
        'items_carrito': carrito.values(),
        'subtotal': subtotal,
        'iva': iva,
        'total': total,
        'esta_vacio': len(carrito) == 0,
    })

def carrito_agregar(request, id):
    # agrega 1 unidad de un paquete al carrito (acepta POST o GET).
    paquete = get_object_or_404(Paquete, id=id)
    carrito = _obtener_carrito(request)
    str_id = str(paquete.id)  

    datos = request.POST if request.method == 'POST' else request.GET
    sin_seleccion = (not datos.getlist('actividades') and not datos.getlist('hoteles') and not datos.getlist('vuelos'))

    if str_id in carrito and sin_seleccion:
        # reutiliza la selección guardada.
        actividades_carrito = carrito[str_id].get('actividades', [])
        hoteles_carrito = carrito[str_id].get('hoteles', [])
        vuelos_carrito = carrito[str_id].get('vuelos', [])
    else:
        # valida cada tipo de selección; ante el primer error vuelve al detalle del paquete.
        actividades, error = _validar_seleccion(
            datos, 'actividades', paquete.itinerarios.order_by('dia', 'horario'),
            MIN_ACTIVIDADES, MAX_ACTIVIDADES, 'actividades')
        if error:
            messages.warning(request, f"{error} Paquete '{paquete.nombre}'.")
            return redirect('catalogo:detalle', paquete.id)

        hoteles, error = _validar_seleccion(
            datos, 'hoteles', paquete.hoteles.order_by('nombre'),
            MIN_HOTELES, MAX_HOTELES, 'hoteles', singular='hotel')
        if error:
            messages.warning(request, f"{error} Paquete '{paquete.nombre}'.")
            return redirect('catalogo:detalle', paquete.id)

        vuelos, error = _validar_seleccion(
            datos, 'vuelos', paquete.vuelos.order_by('fecha_salida', 'hora_salida'),
            MIN_VUELOS, MAX_VUELOS, 'vuelos', singular='vuelo')
        if error:
            messages.warning(request, f"{error} Paquete '{paquete.nombre}'.")
            return redirect('catalogo:detalle', paquete.id)

        # en la sesión solo se guardan datos simples (ids y textos), no objetos del modelo,
        actividades_carrito = [{'id': a.id, 'nombre': a.actividad} for a in actividades]
        hoteles_carrito = [{'id': h.id, 'nombre': h.nombre, 'ciudad': h.ciudad} for h in hoteles]
        vuelos_carrito = [{'id': f.id, 'nombre': f.aerolinea, 'ruta': f"{f.ciudad_origen} → {f.ciudad_destino}"} for f in vuelos]

    # control de cupos: la cantidad en el carrito no puede superar los cupos del paquete.
    cantidad_actual = carrito.get(str_id, {}).get('cantidad', 0)
    nueva_cantidad = cantidad_actual + 1

    if nueva_cantidad > paquete.cupos_disponibles:
        messages.warning(request, f"Límite de cupos alcanzado ({paquete.cupos_disponibles} disponibles) para '{paquete.nombre}'.")
        return redirect('pedidos:ver')

    # se guarda (o reemplaza) el item. El precio queda "congelado" en el carrito
    carrito[str_id] = {
        'id': paquete.id,
        'nombre': paquete.nombre,
        'precio': int(paquete.precio_paquete),
        'cantidad': nueva_cantidad,
        'subtotal': int(paquete.precio_paquete) * nueva_cantidad,
        'actividades': actividades_carrito,
        'hoteles': hoteles_carrito,
        'vuelos': vuelos_carrito,
    }

    request.session.modified = True
    messages.success(request, f"Paquete '{paquete.nombre}' añadido a las reservas.")
    return redirect(request.META.get('HTTP_REFERER') or 'pedidos:ver')

def carrito_restar(request, id):
    # resta 1 unidad; si llega a 0, quita el paquete del carrito
    carrito = _obtener_carrito(request)
    str_id = str(id)
    if str_id in carrito:
        carrito[str_id]['cantidad'] -= 1
        if carrito[str_id]['cantidad'] <= 0:
            del carrito[str_id]
        else:
            # recalcula el subtotal con el precio guardado en el carrito.
            carrito[str_id]['subtotal'] = carrito[str_id]['precio'] * carrito[str_id]['cantidad']
        request.session.modified = True
    return redirect('pedidos:ver')

def carrito_eliminar(request, id):
    # quita un paquete completo del carrito
    carrito = _obtener_carrito(request)
    str_id = str(id)
    if str_id in carrito:
        del carrito[str_id]
        request.session.modified = True
        messages.warning(request, "Paquete eliminado de la lista de reservas.")
    return redirect('pedidos:ver')

def carrito_limpiar(request):
    # vacía el carrito completo
    if 'carrito' in request.session:
        del request.session['carrito']
        request.session.modified = True
    return redirect('pedidos:ver')

@login_requerido_custom   # solo usuarios con sesión iniciada pueden pagar
def checkout_simulado(request):
    # pago simulado (no hay pasarela real). Solo actúa con POST; con GET redirige al carrito.
    if request.method == 'POST':
        carrito = _obtener_carrito(request)
        if not carrito:
            return redirect('catalogo:lista')

        # 'usuario_id' lo guardó el login propio del sitio en la sesión.
        usuario = get_object_or_404(Usuario, id=request.session['usuario_id'])

        # totales para mostrar en la pantalla de éxito (IVA 19%).
        subtotal = sum(item['subtotal'] for item in carrito.values())
        iva = int(subtotal * 0.19)
        total = subtotal + iva
        items_comprados = list(carrito.values())   # copia, porque el carrito se borra al final

        for item in items_comprados:
            paquete = get_object_or_404(Paquete, id=item['id'])

            # Valor de este item con IVA.
            valor_con_iva = item['subtotal'] + int(item['subtotal'] * 0.19)

            # se crea UNA reserva por paquete del carrito (aunque la cantidad sea mayor a 1).
            reserva = Reserva.objects.create(
                usuario=usuario,
                paquete=paquete,
                estado='Pagada',
                precio_total=valor_con_iva
            )

            # se vinculan las opciones elegidas. Se vuelve a filtrar sobre las relaciones del paquete
            ids_actividades = [a['id'] for a in item.get('actividades', [])]
            if ids_actividades:
                reserva.actividades.set(paquete.itinerarios.filter(id__in=ids_actividades))

            ids_hoteles = [h['id'] for h in item.get('hoteles', [])]
            if ids_hoteles:
                reserva.hoteles.set(paquete.hoteles.filter(id__in=ids_hoteles))

            ids_vuelos = [f['id'] for f in item.get('vuelos', [])]
            if ids_vuelos:
                reserva.vuelos.set(paquete.vuelos.filter(id__in=ids_vuelos))

            # pago simulado
            Pago.objects.create(
                reserva=reserva,
                monto=valor_con_iva,
                metodo_pago='Webpay Simulador',
                estado_transaccion='Aprobada'
            )

            # descuento de cupos de paquete turístico
            if paquete.cupos_disponibles >= item['cantidad']:
                paquete.cupos_disponibles -= item['cantidad']
                paquete.save()

        # compra terminada: se vacía el carrito
        del request.session['carrito']
        request.session.modified = True

        return render(request, 'pedidos/checkout_exito.html', {
            'items': items_comprados,
            'subtotal': subtotal,
            'iva': iva,
            'total': total,
            'orden_id': f"RES-{usuario.id}-2026",
        })

    # GET (u otro método): no se paga nada, se vuelve al carrito.
    return redirect('pedidos:ver')