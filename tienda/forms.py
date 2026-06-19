from django import forms
from .models import Producto, Pedido, Categoria

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields =["nombre", "descripcion","precio", "categoria","imagen","disponible", "destacado"
                 ]

class CheckoutForm(forms.ModelForm):
    class Meta: 
        model = Pedido
        fields = ["tipo_entrega", "direccion_entrega", "telefono", "notas"]

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion", "activa"]
        