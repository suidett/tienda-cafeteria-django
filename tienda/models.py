from django.db import models
from django.contrib.auth.models import User  # el modelo de usuario que trae Django


class Categoria(models.Model):
    """Categoría de productos: Cafés calientes, Postres, Sándwiches, etc."""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Un producto que vende la cafetería (un café, un postre, un sándwich...)."""
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits = 8, decimal_places=2)

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="productos",
    )
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)
    disponible = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    # aca se ve quien hace el pedido
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EN_PREPARACION = "en_preparacion", "En preparación"
        LISTO = "listo", "Listo"
        ENTREGADO = "entregado", "Entregado"
        CANCELADO = "cancelado", "Cancelado"

    class TipoEntrega(models.TextChoices):
        RETIRO = "retiro", "Retiro en local"
        DELIVERY = "delivery", "Delivery"

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="pedidos")
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    tipo_entrega = models.CharField(max_length=20, choices=TipoEntrega.choices, default=TipoEntrega.RETIRO)
    direccion_entrega = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    notas = models.TextField(blank=True, help_text="Observaciones del cliente")
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-creado"]

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username if self.usuario else 'Invitado'}"

    def total(self):
        return sum(detalle.subtotal() for detalle in self.detalles.all())


class DetallePedido(models.Model):
    """Una línea del pedido: '2 x Café Latte'. Conecta un Pedido con un Producto."""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="detalles_pedido")
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.PositiveIntegerField(help_text="Precio al momento de la compra (CLP)")

    class Meta:
        verbose_name = "Detalle de pedido"
        verbose_name_plural = "Detalles de pedido"

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    def subtotal(self):
        return self.cantidad * self.precio_unitario

