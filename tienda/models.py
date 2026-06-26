from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User  # el modelo de usuario que trae Django


# ─── TABLA 1: Categoría ─── agrupa los productos (Cafés, Postres, etc.)
class Categoria(models.Model):
    """Categoría de productos: Cafés calientes, Postres, Sándwiches, etc."""
    nombre = models.CharField(max_length=100, unique=True)  # nombre (no se puede repetir)
    descripcion = models.TextField(blank=True)              # texto opcional
    activa = models.BooleanField(default=True)              # si está activa, se muestra en la carta

    class Meta:
        verbose_name = "Categoría"          # nombre bonito en singular (para el admin)
        verbose_name_plural = "Categorías"  # nombre bonito en plural
        ordering = ["nombre"]               # las muestra ordenadas por nombre

    def __str__(self):
        return self.nombre  # lo que se ve cuando mostramos una categoría


# ─── TABLA 2: Producto ─── cada café / postre / sándwich que se vende
class Producto(models.Model):
    """Un producto que vende la cafetería (un café, un postre, un sándwich...)."""
    nombre = models.CharField(max_length=150)    # nombre del producto
    descripcion = models.TextField(blank=True)   # descripción opcional
    precio = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(1)])  # precio (mínimo 1)

    # cada producto pertenece a UNA categoría (relación 1 a muchos)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,        # PROTECT = no deja borrar una categoría si tiene productos
        related_name="productos",        # permite hacer: categoria.productos.all()
    )
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)  # foto (opcional)
    disponible = models.BooleanField(default=True)   # si está disponible para comprar
    destacado = models.BooleanField(default=False)   # si se muestra como destacado
    creado = models.DateTimeField(auto_now_add=True)  # guarda la fecha de creación sola

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]  # ordenados por nombre

    def __str__(self):
        return self.nombre


# ─── TABLA 3: Pedido ─── una compra hecha por un cliente (o invitado)
class Pedido(models.Model):
    # aca se ve quien hace el pedido

    # las opciones de estado del pedido (lista cerrada de valores permitidos)
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EN_PREPARACION = "en_preparacion", "En preparación"
        LISTO = "listo", "Listo"
        ENTREGADO = "entregado", "Entregado"
        CANCELADO = "cancelado", "Cancelado"

    # cómo recibe el pedido el cliente
    class TipoEntrega(models.TextChoices):
        RETIRO = "retiro", "Retiro en local"
        DELIVERY = "delivery", "Delivery"

    # cómo paga el cliente
    class ModoPago(models.TextChoices):
        ONLINE = "online", "Pagado online (Mercado Pago)"
        LOCAL = "local", "Pago al retirar"

    # quién hizo el pedido. SET_NULL = si se borra el usuario, el pedido queda como "Invitado"
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="pedidos")
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)  # estado actual
    tipo_entrega = models.CharField(max_length=20, choices=TipoEntrega.choices, default=TipoEntrega.RETIRO)
    direccion_entrega = models.CharField(max_length=255, blank=True)  # solo si es delivery
    telefono = models.CharField(max_length=20, blank=True)            # teléfono de contacto
    nombre_contacto = models.CharField(max_length=120, blank=True)    # nombre de quien retira
    hora_retiro = models.CharField(max_length=40, blank=True)         # horario elegido para retirar
    modo_pago = models.CharField(max_length=10, choices=ModoPago.choices, default=ModoPago.LOCAL)
    notas = models.TextField(blank=True, help_text="Observaciones del cliente")
    creado = models.DateTimeField(auto_now_add=True)   # fecha en que se hizo el pedido
    actualizado = models.DateTimeField(auto_now=True)  # fecha de la última modificación

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-creado"]  # el "-" los muestra del más nuevo al más viejo

    def __str__(self):
        # muestra "Pedido #3 - cliente" (o "Invitado" si no hay usuario)
        return f"Pedido #{self.id} - {self.usuario.username if self.usuario else 'Invitado'}"

    def total(self):
        # suma los subtotales de todas las líneas del pedido
        return sum(detalle.subtotal() for detalle in self.detalles.all())


# ─── TABLA 4: DetallePedido ─── cada línea de un pedido ("2 x Café Latte")
class DetallePedido(models.Model):
    """Una línea del pedido: '2 x Café Latte'. Conecta un Pedido con un Producto."""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="detalles")  # CASCADE = si se borra el pedido, se borran sus líneas
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="detalles_pedido")  # PROTECT = no deja borrar un producto que está en pedidos
    cantidad = models.PositiveIntegerField(default=1)  # cuántas unidades
    precio_unitario = models.PositiveIntegerField(help_text="Precio al momento de la compra (CLP)")  # guarda el precio de ESE momento (el historial no cambia si suben el precio después)

    class Meta:
        verbose_name = "Detalle de pedido"
        verbose_name_plural = "Detalles de pedido"

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    def subtotal(self):
        # precio de esta línea = cantidad x precio unitario
        return self.cantidad * self.precio_unitario
