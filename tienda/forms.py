import re
from datetime import datetime, time, timedelta
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import Producto, Pedido, Categoria


# --- Horario de retiro del local (configurable) ---
HORA_APERTURA = 9    # abre 09:00
HORA_CIERRE = 19     # último retiro 19:00
PASO_MIN = 30        # turnos cada 30 minutos
MARGEN_MIN = 30      # anticipación mínima para preparar el pedido
DIAS_ADELANTE = 2    # genera turnos para hoy y mañana


def generar_slots_retiro():
    """Horas de retiro disponibles cada PASO_MIN minutos, desde (ahora + MARGEN_MIN)
    hasta el cierre, para los próximos DIAS_ADELANTE días. Se recalcula en cada request."""
    ahora = timezone.localtime()
    minimo = ahora + timedelta(minutes=MARGEN_MIN)
    slots = []
    for d in range(DIAS_ADELANTE):
        dia = (ahora + timedelta(days=d)).date()
        actual = timezone.make_aware(datetime.combine(dia, time(HORA_APERTURA, 0)))
        cierre = timezone.make_aware(datetime.combine(dia, time(HORA_CIERRE, 0)))
        while actual <= cierre:
            if actual >= minimo:
                etiqueta = "Hoy" if d == 0 else ("Mañana" if d == 1 else actual.strftime("%d/%m"))
                slots.append((actual.strftime("%d/%m %H:%M"), f"{etiqueta} {actual.strftime('%H:%M')}"))
            actual += timedelta(minutes=PASO_MIN)
    return slots

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields =["nombre", "descripcion","precio", "categoria","imagen","disponible", "destacado"
                 ]

class CheckoutForm(forms.ModelForm):
    hora_retiro = forms.ChoiceField(label="Hora de retiro")

    class Meta:
        model = Pedido
        fields = ["nombre_contacto", "telefono", "hora_retiro", "notas"]
        labels = {
            "nombre_contacto": "Nombre",
            "telefono": "Teléfono",
            "notas": "Notas (opcional)",
        }
        widgets = {
            "nombre_contacto": forms.TextInput(attrs={"placeholder": "Tu nombre"}),
            "telefono": forms.TextInput(attrs={"placeholder": "+56 9 1234 5678"}),
            "notas": forms.Textarea(attrs={"rows": 2, "placeholder": "¿Algo que debamos saber?"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nombre_contacto"].required = True
        self.fields["telefono"].required = True
        self.fields["hora_retiro"].choices = [("", "Elegí un horario")] + generar_slots_retiro()

    def clean_telefono(self):
        telefono = self.cleaned_data["telefono"]
        digitos = re.sub(r"\D", "", telefono)

        # Si lo escriben con código de país (+56), lo sacamos para validar el número nacional
        if digitos.startswith("56"):
            digitos = digitos[2:]

        # Celular chileno: 9 dígitos que empiezan con 9
        if len(digitos) != 9 or not digitos.startswith("9"):
            raise forms.ValidationError("Ingresá un celular chileno válido: +56 9 XXXX XXXX.")

        return telefono

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion", "activa"]


class RecuperarPasswordForm(forms.Form):
    username = forms.CharField(label="Usuario", max_length=150)
    email = forms.EmailField(label="Email")
    password1 = forms.CharField(label="Nueva contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Repetir contraseña", widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("No existe un usuario con ese nombre.")
        return username

    def clean_password1(self):
        password = self.cleaned_data["password1"]
        validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned
        