from django.urls import path
from . import views

# app_name crea un "namespace": en plantillas y redirecciones las rutas se referencian
app_name = 'core'

urlpatterns = [
    # ruta vacía = raíz de la app: portada del sitio.
    path('', views.inicio, name='inicio'),
    # página 'Quienes Somos' estática.
    path('nosotros/', views.nosotros, name='nosotros'),
]