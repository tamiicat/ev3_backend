from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.catalogo.models import Paquete
from apps.usuarios.models import Usuario
from apps.pedidos.models import Reserva, Pago
from apps.usuarios.views import login_requerido_custom

def _obtener_carrito(request):
    return request.session.setdefault('carrito', {})

def carrito_ver(request):
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
    paquete = get_object_or_404(Paquete, id=id)
    carrito = _obtener_carrito(request)
    str_id = str(paquete.id)

    cantidad_actual = carrito.get(str_id, {}).get('cantidad', 0)
    nueva_cantidad = cantidad_actual + 1

    if nueva_cantidad > paquete.cupos_disponibles:
        messages.warning(request, f"Límite de cupos alcanzado ({paquete.cupos_disponibles} disponibles) para '{paquete.nombre}'.")
        return redirect('pedidos:ver')

    carrito[str_id] = {
        'id': paquete.id,
        'nombre': paquete.nombre,
        'precio': int(paquete.precio_paquete),
        'cantidad': nueva_cantidad,
        'subtotal': int(paquete.precio_paquete) * nueva_cantidad,
    }

    request.session.modified = True
    messages.success(request, f"Paquete '{paquete.nombre}' añadido a las reservas.")
    return redirect(request.META.get('HTTP_REFERER') or 'pedidos:ver')

def carrito_restar(request, id):
    carrito = _obtener_carrito(request)
    str_id = str(id)
    if str_id in carrito:
        carrito[str_id]['cantidad'] -= 1
        if carrito[str_id]['cantidad'] <= 0:
            del carrito[str_id]
        else:
            carrito[str_id]['subtotal'] = carrito[str_id]['precio'] * carrito[str_id]['cantidad']
        request.session.modified = True
    return redirect('pedidos:ver')

def carrito_eliminar(request, id):
    carrito = _obtener_carrito(request)
    str_id = str(id)
    if str_id in carrito:
        del carrito[str_id]
        request.session.modified = True
        messages.warning(request, "Paquete eliminado de la lista de reservas.")
    return redirect('pedidos:ver')

def carrito_limpiar(request):
    if 'carrito' in request.session:
        del request.session['carrito']
        request.session.modified = True
    return redirect('pedidos:ver')

@login_requerido_custom
def checkout_simulado(request):
    if request.method == 'POST':
        carrito = _obtener_carrito(request)
        if not carrito:
            return redirect('catalogo:lista')

        usuario = get_object_or_404(Usuario, id=request.session['usuario_id'])
        
        subtotal = sum(item['subtotal'] for item in carrito.values())
        iva = int(subtotal * 0.19)
        total = subtotal + iva
        items_comprados = list(carrito.values())

        for item in items_comprados:
            paquete = get_object_or_404(Paquete, id=item['id'])

            valor_con_iva = item['subtotal'] + int(item['subtotal'] * 0.19)

            reserva = Reserva.objects.create(
                usuario=usuario,
                paquete=paquete,
                estado='Pagada',
                precio_total=valor_con_iva
            )

            Pago.objects.create(
                reserva=reserva,
                monto=valor_con_iva,
                metodo_pago='Webpay Simulador',
                estado_transaccion='Aprobada'
            )

            if paquete.cupos_disponibles >= item['cantidad']:
                paquete.cupos_disponibles -= item['cantidad']
                paquete.save()

        del request.session['carrito']
        request.session.modified = True

        return render(request, 'pedidos/checkout_exito.html', {
            'items': items_comprados,
            'subtotal': subtotal,
            'iva': iva,
            'total': total,
            'orden_id': f"RES-{usuario.id}-2026",
        })
        
    return redirect('pedidos:ver')