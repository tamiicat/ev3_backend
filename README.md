# Evaluación 3 - Backend

| Concepto | Detalle |
| :--- | :--- |
| **Nombre de la Plataforma** | Nómade |
| **Modelo de Negocio** | Agencia de paquetes turísticos |
| **Integrantes** | Vicente Cabrera: 21.014.795-0 - Tamara Soto: 20.515.480-9 |
| **Entidad de Contexto** | Categoría de Destino |
| **Entidad Principal Gestionable (ORM)** | Paquete Turístico |
| **Propósito de la Sesión (request.session)** | Carrito de Reservas |

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu sistema:
*   **Python 3.10+**
*   **Git**

## Instalación y Ejecución Paso a Paso

Sigue estos pasos en tu terminal para ejecutar el proyecto de forma local sin problemas de dependencias:

**1. Clonar el repositorio**\
git clone https://github.com/tamiicat/ev3_backend.git

cd ev3_backend

**2. Crear y activar el entorno virtual**\
En Windows (PowerShell/CMD):\
python -m venv venv venv\Scripts\activate

En macOS/Linux:\
python3 -m venv venv source venv/bin/activate

**3. Instalar las dependencias**\
pip install -r requirements.txt

**4. Aplicar las migraciones de la Base de Datos**\
python manage.py makemigrations\
python manage.py migrate

**5. Poblar la Base de Datos (Opcional pero Recomendado)**\
python manage.py poblar_nomade

**6. Iniciar el Servidor de Desarrollo**\
python manage.py runserver

Abrir navegador web y visitar: http://127.0.0.1:8000/

## Credenciales de Acceso
**Usuario Administrador**
*   Correo Electrónico: admin@nomade.cl
*   Password: admin

**Super Usuarios**\
Usuario: vicente
*   Correo Electrónico: in.cabrera1010@gmail.com
*   Password: password1010

Usuario: tamara
*   Correo Electrónico: tamaraaguayo11@gmail.com
*   Password: password987

## Bitácora de IA

**Prompt Arquitectura**
> "Para nuestro proyecto 'Nómade' (agencia de paquetes turísticos), ¿cuál sería la entidad de contexto más apropiada basándonos en nuestro catálogo de ideas? Inicialmente definimos 'GestionViajes' como contexto y 'Turismo' como entidad principal gestionable."

*   Respuesta Técnica:
>"Nuestro planteamiento inicial de usar "GestionViajes" era conceptualmente erróneo para la base de datos. La IA nos ayudó a corregir la arquitectura definiendo "Categoría de Destino" (continentes/regiones) como la Entidad de Contexto y "Paquete Turístico" como la Entidad Principal."

*   Adaptación Aplicada:
>"Se modificó el archivo `admin.py` adaptando la clase `PaqueteAdmin`. Implementamos tuplas de `fieldsets` para modularizar la vista del formulario, usamos `filter_horizontal` para las relaciones M a M (hoteles y vuelos), y ajustamos los filtros laterales para cumplir con los estándares de administración avanzada solicitados."

**Prompt ORM**
> "Modifica el archivo `poblar_nomade.py` usando el ORM de Django para que genere datos de prueba automáticos para nuestro proyecto. Necesito que cree un usuario administrador (con las credenciales de siempre), categorías de destino con nombres de continentes, y servicios base consistentes en 4 paquetes turísticos (con imagen incluida). Además, utiliza el ORM para asociar dinámicamente a cada paquete: 2 hoteles (destino), 7 actividades de itinerario y 4 vuelos disponibles."

*   Respuesta Técnica:
>"Poblar datos relacionales manualmente desde el panel de administración para realizar pruebas es ineficiente y propenso a errores. Necesitábamos un script robusto que manejara múltiples tipos de relaciones simultáneamente."

*   Adaptación Aplicada:
>"Adaptamos el código sugerido en nuestro comando personalizado `apps/catalogo/management/commands/poblar_nomade.py`. Utilizamos los métodos del ORM `.create()` para entidades independientes e iteraciones con `.add()` para enlazar correctamente las relaciones M a M (Hoteles y Vuelos) y las claves foráneas (Itinerarios) a cada paquete instanciado, garantizando la integridad referencial de la base de datos de prueba."

**Prompt Seguridad**
> "Dado que en nuestro proyecto Nómade implementamos un inicio de sesión manual personalizado usando variables como `request.session['usuario_id']` en lugar del sistema auth por defecto de Django, ¿cómo podemos proteger de forma segura las vistas privadas (como el perfil y el carrito) mediante un decorador para evitar vulnerabilidades de acceso directo si alguien escribe la URL en el navegador?"

*   Respuesta Técnica:
>"Al prescindir del framework clásico `@login_required` de Django, nuestras vistas requerían una validación explícita para evitar que usuarios no autenticados accedieran a información confidencial o realizaran compras."

*   Adaptación Aplicada:
>"Desarrollamos un decorador propio (`@login_requerido_custom`) en el archivo `usuarios/views.py`. Este decorador intercepta las solicitudes HTTP, verifica la existencia de la variable `usuario_id` en el diccionario de sesión, y fuerza una redirección HTTP 302 hacia el login si la sesión no es válida, aislando la capa de datos del cliente de forma segura."