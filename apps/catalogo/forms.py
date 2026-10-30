from django import forms
from .models import Paquete

class PaqueteForm(forms.ModelForm):
    class Meta:
        model = Paquete
        fields = [
            'nombre', 'categoria', 'descripcion', 'precio_paquete', 
            'cupos_disponibles', 'fecha_inicio', 'fecha_fin', 
            'estado', 'imagen', 'activo', 'hoteles', 'vuelos'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Tour por Europa de 10 días'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción del viaje...'}),
            'precio_paquete': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'cupos_disponibles': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'hoteles': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'vuelos': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def clean_precio_paquete(self):
        precio = self.cleaned_data.get('precio_paquete')
        if precio is not None and precio <= 0:
            raise forms.ValidationError("El precio del paquete debe ser superior a 0 CLP.")
        return precio