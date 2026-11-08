from django import forms
from .models import Paquete, Itinerario, Hotel, Vuelo

class PaqueteForm(forms.ModelForm):
    # formulario para crear paquetes turísticos
    class Meta:
        model = Paquete
        # incluyen: el slug se genera solo y el estado queda en su valor por defecto.
        fields = [
            'nombre', 'categoria', 'descripcion', 'precio_paquete',
            'cupos_disponibles', 'fecha_inicio', 'fecha_fin',
            'imagen', 'activo', 'hoteles', 'vuelos'
        ]
        labels = {
            'nombre': 'Nombre del Paquete',
            'categoria': 'Continente / Región',
            'descripcion': 'Descripción del Viaje',
            'precio_paquete': 'Precio en CLP',
            'cupos_disponibles': 'Cupos disponibles',
            'fecha_inicio': 'Fecha de inicio',
            'fecha_fin': 'Fecha de término',
            'imagen': 'Fotografía del destino',
            'activo': '¿Disponible?',
            'hoteles': 'Hoteles incluidos',
            'vuelos': 'Vuelos incluidos',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Tour por Europa de 10 días'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción del viaje...'}),
            'precio_paquete': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'cupos_disponibles': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'fecha_inicio': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'hoteles': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'vuelos': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def clean_precio_paquete(self):
        # validación de un campo, se ejecuta automáticamente para 'precio_paquete'
        precio = self.cleaned_data.get('precio_paquete')
        if precio is not None and precio <= 0:
            raise forms.ValidationError("El precio del paquete debe ser superior a 0 CLP.")
        return precio

    def clean(self):
        # validación de varios campos
        cleaned = super().clean()
        inicio, fin = cleaned.get('fecha_inicio'), cleaned.get('fecha_fin')
        if inicio and fin and fin < inicio:
            self.add_error('fecha_fin', "La fecha de término no puede ser anterior a la de inicio.")
        return cleaned

class ItinerarioForm(forms.ModelForm):
    # formulario para agregar/editar una actividad del itinerario
    class Meta:
        model = Itinerario
        fields = ['paquete', 'dia', 'actividad', 'descripcion', 'horario']
        labels = {
            'paquete': 'Paquete Turístico',
            'dia': 'Fecha de la actividad',
            'actividad': 'Nombre de la Actividad',
            'descripcion': 'Descripción detallada',
            'horario': 'Horario (HH:MM)'
        }
        widgets = {
            'paquete': forms.Select(attrs={'class': 'form-select'}),
            'dia': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'actividad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Visita al museo histórico'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detalles del punto de encuentro y la actividad...'}),
            'horario': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'type': 'time'}),
        }

class HotelForm(forms.ModelForm):
    # formulario de hotel
    paquetes = forms.ModelMultipleChoiceField(
        queryset=Paquete.objects.all().order_by('nombre'),   # opciones disponibles
        required=False,                                      # puede quedar sin paquetes
        label='Paquetes donde se incluye',
        help_text='Mantén presionada la tecla Ctrl (o Cmd) para seleccionar varios paquetes.',
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 6}),
    )

    class Meta:
        model = Hotel
        fields = ['nombre', 'ciudad', 'direccion', 'categoria', 'habitacion', 'servicios']
        labels = {
            'nombre': 'Nombre del Hotel',
            'ciudad': 'Ciudad',
            'direccion': 'Dirección',
            'categoria': 'Categoría',
            'habitacion': 'Cantidad de habitaciones',
            'servicios': '¿Incluye servicios adicionales?',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Inca Imperial'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Cusco'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Calle Ruinas 465'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'habitacion': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'servicios': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['paquetes'].initial = self.instance.paquetes.all()

    def clean_habitacion(self):
        # validación para que la cantidad de habitaciones sea positiva
        habitacion = self.cleaned_data.get('habitacion')
        if habitacion is not None and habitacion <= 0:
            raise forms.ValidationError("La cantidad de habitaciones debe ser mayor a 0.")
        return habitacion

    def save(self, commit=True):
        # guarda hotel
        hotel = super().save(commit=commit)
        if commit:
            hotel.paquetes.set(self.cleaned_data['paquetes'])
        return hotel

class VueloForm(forms.ModelForm):
    # formulario de vuelo
    paquetes = forms.ModelMultipleChoiceField(
        queryset=Paquete.objects.all().order_by('nombre'),
        required=False,
        label='Paquetes donde se incluye',
        help_text='Mantén presionada la tecla Ctrl (o Cmd) para seleccionar varios paquetes.',
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 6}),
    )

    class Meta:
        model = Vuelo
        fields = [
            'aerolinea', 'ciudad_origen', 'ciudad_destino',
            'fecha_salida', 'hora_salida', 'fecha_llegada', 'hora_llegada',
        ]
        labels = {
            'aerolinea': 'Aerolínea',
            'ciudad_origen': 'Ciudad de origen',
            'ciudad_destino': 'Ciudad de destino',
            'fecha_salida': 'Fecha de salida',
            'hora_salida': 'Hora de salida (HH:MM)',
            'fecha_llegada': 'Fecha de llegada',
            'hora_llegada': 'Hora de llegada (HH:MM)',
        }
        widgets = {
            'aerolinea': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Sky Airlines'}),
            'ciudad_origen': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Santiago'}),
            'ciudad_destino': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Cusco'}),
            'fecha_salida': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'hora_salida': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'type': 'time'}),
            'fecha_llegada': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'hora_llegada': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['paquetes'].initial = self.instance.paquetes.all()

    def clean(self):
        # validaciones cruzadas entre origen/destino y fechas/horas."""
        cleaned = super().clean()

        # origen y destino
        origen = (cleaned.get('ciudad_origen') or '').strip().lower()
        destino = (cleaned.get('ciudad_destino') or '').strip().lower()
        if origen and destino and origen == destino:
            self.add_error('ciudad_destino', "El destino no puede ser igual al origen.")

        # coherencia entre fechas y horas
        f_sal, h_sal = cleaned.get('fecha_salida'), cleaned.get('hora_salida')
        f_lle, h_lle = cleaned.get('fecha_llegada'), cleaned.get('hora_llegada')
        if f_sal and f_lle:
            if f_lle < f_sal:
                # selección inválida: llegada en un día anterior a la salida (imposible).
                self.add_error('fecha_llegada', "La llegada no puede ser anterior a la salida.")
            elif f_lle == f_sal and h_sal and h_lle and h_lle <= h_sal:
                # en caso del mismo día: la hora de llegada debe ser posterior a la de salida.
                self.add_error('hora_llegada', "La hora de llegada debe ser posterior a la de salida.")
        return cleaned

    def save(self, commit=True):
        # guarda el vuelo
        vuelo = super().save(commit=commit)
        if commit:
            vuelo.paquetes.set(self.cleaned_data['paquetes'])
        return vuelo