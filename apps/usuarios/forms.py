import re
from django import forms
from .models import Usuario

class RegistroForm(forms.ModelForm):
    contrasena = forms.CharField(
        label="Contraseña", 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    # teléfono con codigo de Chile (+56) y validación de solo dígitos
    telefono = forms.CharField(
        label="Teléfono",
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'tel',
            'inputmode': 'numeric',
            'placeholder': '987654321',
            'maxlength': '9',
            'oninput': "this.value = this.value.replace(/\\D/g, '')",  # solo dígitos
        }),
    )

    class Meta:
        model = Usuario
        fields = ['rut', 'nombre', 'apellido', 'telefono', 'correo_electronico', 'contrasena']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 12345678-9'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_electronico': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        
    def clean_correo_electronico(self):
        email = self.cleaned_data.get('correo_electronico')
        if Usuario.objects.filter(correo_electronico=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if Usuario.objects.filter(rut=rut).exists():
            raise forms.ValidationError("Este RUT ya está registrado.")
        return rut

    def clean_telefono(self):
        # valida un celular chileno y lo normaliza al formato +569XXXXXXXX
        tel = re.sub(r'[\s\-\(\)]', '', self.cleaned_data.get('telefono', ''))
        # acepta que peguen el número con +56 o 56 delante
        if tel.startswith('+56'):
            tel = tel[3:]
        elif tel.startswith('56') and len(tel) == 11:
            tel = tel[2:]
        if not re.fullmatch(r'9\d{8}', tel):
            raise forms.ValidationError(
                "Ingresa un celular chileno válido: 9 dígitos que comiencen con 9 (ej. 9 1234 5678)."
            )
        return f'+56{tel}'

    def save(self, commit=True):
        # se cifra la contraseña ANTES de guardar
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['contrasena'])
        if commit:
            usuario.save()
        return usuario


class LoginForm(forms.Form):
    correo_electronico = forms.EmailField(
        label="Correo Electrónico", 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    contrasena = forms.CharField(
        label="Contraseña", 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )