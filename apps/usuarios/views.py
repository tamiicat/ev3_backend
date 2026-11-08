from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from functools import wraps
from .forms import RegistroForm, LoginForm
from .models import Usuario
from apps.catalogo.models import Resena

def login_requerido_custom(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            messages.warning(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('usuarios:login')
        return view_func(request, *args, **kwargs)
    return wrapper

def registro_usuario(request):
    # quien ya tiene sesión no necesita registrarse de nuevo.
    if request.session.get('usuario_id'):
        return redirect('catalogo:lista')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.rol = 'cliente'
            usuario.save()

            # inicia sesión automáticamente tras registrarse
            request.session['usuario_id'] = usuario.id
            request.session['usuario_rol'] = usuario.rol
            request.session['usuario_nombre'] = usuario.nombre
            messages.success(request, f"¡Bienvenido {usuario.nombre}! Cuenta creada.")
            return redirect('catalogo:lista')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

def _destino_seguro(request, destino):
    if not destino:
        return 'catalogo:lista'
    if destino.startswith('/'):
        if url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()}):
            return destino
        return 'catalogo:lista'
    return destino

def login_usuario(request):
    if request.session.get('usuario_id'):
        return redirect('catalogo:lista')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data.get('correo_electronico')
            contrasena = form.cleaned_data.get('contrasena')
            usuario = Usuario.objects.filter(correo_electronico=correo).first()
            if usuario and usuario.check_password(contrasena):
                request.session['usuario_id'] = usuario.id
                request.session['usuario_rol'] = usuario.rol
                request.session['usuario_nombre'] = usuario.nombre
                messages.success(request, f"¡Bienvenido {usuario.nombre}! Sesión iniciada correctamente.")
                return redirect(_destino_seguro(request, request.POST.get('next')))
            # mensaje: no revela si falló el correo o la contraseña.
            messages.error(request, "Correo o contraseña incorrectos.")
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form, 'next': request.GET.get('next', 'catalogo:lista')})

def logout_usuario(request):
    # flush() borra TODA la sesión: datos de usuario y también el carrito.
    request.session.flush()
    messages.info(request, "Has cerrado sesión.")
    return redirect('core:inicio')

@login_requerido_custom
def perfil_usuario(request):
    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    # select_related('paquete') trae el paquete de cada reserva en la misma consulta
    reservas = list(usuario.reservas.select_related('paquete').order_by('-fecha'))
    # diccionario con las reseñas que este usuario ya escribió.
    resenas = {r.paquete_id: r for r in Resena.objects.filter(usuario=usuario)}
    for reserva in reservas:
        reserva.resena = resenas.get(reserva.paquete_id)

    return render(request, 'usuarios/perfil.html', {
        'usuario': usuario,
        'reservas': reservas,
    })