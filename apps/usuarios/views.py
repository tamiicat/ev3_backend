from django.shortcuts import render, redirect
from django.contrib import messages
from functools import wraps
from .forms import RegistroForm, LoginForm
from .models import Usuario

def login_requerido_custom(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            messages.warning(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('usuarios:login')
        return view_func(request, *args, **kwargs)
    return wrapper

def registro_usuario(request):
    if request.session.get('usuario_id'):
        return redirect('catalogo:lista')
        
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.rol = 'cliente'
            usuario.save()

            request.session['usuario_id'] = usuario.id
            request.session['usuario_rol'] = usuario.rol
            messages.success(request, f"¡Bienvenido {usuario.nombre}! Cuenta creada.")
            return redirect('catalogo:lista')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

def login_usuario(request):
    if request.session.get('usuario_id'):
        return redirect('catalogo:lista')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data.get('correo_electronico')
            contrasena = form.cleaned_data.get('contrasena')
            
            try:
                usuario = Usuario.objects.get(correo_electronico=correo, contrasena=contrasena)
                request.session['usuario_id'] = usuario.id
                request.session['usuario_rol'] = usuario.rol
                messages.success(request, f"¡Bienvenido {usuario.nombre}! Sesión iniciada correctamente.")
                return redirect(request.POST.get('next') or 'catalogo:lista')
            except Usuario.DoesNotExist:
                messages.error(request, "Correo o contraseña incorrectos.")
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form, 'next': request.GET.get('next', 'catalogo:lista')})

def logout_usuario(request):
    request.session.flush() 
    messages.info(request, "Has cerrado sesión.")
    return redirect('core:inicio')

@login_requerido_custom
def perfil_usuario(request):
    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    return render(request, 'usuarios/perfil.html', {'usuario': usuario})