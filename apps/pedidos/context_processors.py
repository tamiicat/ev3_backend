# un context processor es una función que recibe el request y devuelve un diccionario;
def carrito_context(request):
    # entrega la cantidad total de paquetes en el carrito
    carrito = request.session.get('carrito', {})
    # suma el campo 'cantidad' de cada item (si faltara, cuenta 0).
    total_items = sum(item.get('cantidad', 0) for item in carrito.values())
    return {
        'carrito_total_items': total_items
    }