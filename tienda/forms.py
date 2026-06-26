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
    ahora = timezone.localtime()  # la hora actual
    minimo = ahora + timedelta(minutes=MARGEN_MIN)  # desde cuándo se puede retirar
    slots = []
    for d in range(DIAS_ADELANTE):  # para hoy y mañana
        dia = (ahora + timedelta(days=d)).date()
        actual = timezone.make_aware(datetime.combine(dia, time(HORA_APERTURA, 0)))  # arranca en la apertura
        cierre = timezone.make_aware(datetime.combine(dia, time(HORA_CIERRE, 0)))    # hasta el cierre
        while actual <= cierre:  # va sumando turnos cada PASO_MIN minutos
            if actual >= minimo:  # solo turnos que todavía no pasaron
                etiqueta = "Hoy" if d == 0 else ("Mañana" if d == 1 else actual.strftime("%d/%m"))
                slots.append((actual.strftime("%d/%m %H:%M"), f"{etiqueta} {actual.strftime('%H:%M')}"))
            actual += timedelta(minutes=PASO_MIN)
    return slots  # lista de horarios para el menú desplegable

# Formulario para crear/editar PRODUCTOS (lo usa el admin)
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto  # se arma solo a partir del modelo Producto
        fields =["nombre", "descripcion","precio", "categoria","imagen","disponible", "destacado"
                 ]  # los campos que pide el formulario

# Formulario del CHECKOUT (datos para finalizar la compra)
class CheckoutForm(forms.ModelForm):
    hora_retiro = forms.ChoiceField(label="Hora de retiro")  # menú desplegable con los horarios

    class Meta:
        model = Pedido
        fields = ["nombre_contacto", "telefono", "hora_retiro", "notas"]  # campos que se le piden al cliente
        labels = {  # los nombres bonitos que ve el usuario
            "nombre_contacto": "Nombre",
            "telefono": "Teléfono",
            "notas": "Notas (opcional)",
        }
        widgets = {  # cómo se ve cada campo (textos de ejemplo)
            "nombre_contacto": forms.TextInput(attrs={"placeholder": "Tu nombre"}),
            "telefono": forms.TextInput(attrs={"placeholder": "+56 9 1234 5678"}),
            "notas": forms.Textarea(attrs={"rows": 2, "placeholder": "¿Algo que debamos saber?"}),
        }

    def __init__(self, *args, **kwargs):
        # se ejecuta al crear el formulario: prepara los campos
        super().__init__(*args, **kwargs)
        self.fields["nombre_contacto"].required = True  # el nombre es obligatorio
        self.fields["telefono"].required = True         # el teléfono es obligatorio
        self.fields["hora_retiro"].choices = [("", "Elegí un horario")] + generar_slots_retiro()  # carga los horarios

    def clean_telefono(self):
        # VALIDACIÓN: solo acepta celular chileno (+56 9 XXXX XXXX)
        telefono = self.cleaned_data["telefono"]
        digitos = re.sub(r"\D", "", telefono)  # deja solo los números (saca +, espacios, guiones)

        # Si lo escriben con código de país (+56), lo sacamos para validar el número nacional
        if digitos.startswith("56"):
            digitos = digitos[2:]

        # Celular chileno: 9 dígitos que empiezan con 9
        if len(digitos) != 9 or not digitos.startswith("9"):
            raise forms.ValidationError("Ingresá un celular chileno válido: +56 9 XXXX XXXX.")  # corta y muestra el error

        return telefono  # si pasó la validación, devuelve el teléfono

# Formulario para crear/editar CATEGORÍAS (lo usa el admin)
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion", "activa"]  # campos de la categoría


# Formulario para RECUPERAR CONTRASEÑA
class RecuperarPasswordForm(forms.Form):
    username = forms.CharField(label="Usuario", max_length=150)
    email = forms.EmailField(label="Email")  # EmailField valida que tenga formato de email
    password1 = forms.CharField(label="Nueva contraseña", widget=forms.PasswordInput)  # PasswordInput = oculta lo que se escribe
    password2 = forms.CharField(label="Repetir contraseña", widget=forms.PasswordInput)

    def clean_username(self):
        # VALIDACIÓN: el usuario tiene que existir
        username = self.cleaned_data["username"]
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("No existe un usuario con ese nombre.")
        return username

    def clean_password1(self):
        # VALIDACIÓN: la contraseña tiene que cumplir las reglas de Django (largo, etc.)
        password = self.cleaned_data["password1"]
        validate_password(password)
        return password

    def clean(self):
        # VALIDACIÓN final: las dos contraseñas tienen que coincidir
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned
