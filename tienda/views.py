from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages 
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import Categoria, Producto, Pedido, DetallePedido
from .forms import ProductoForm, CheckoutForm, CategoriaForm, RecuperarPasswordForm
from django.contrib.auth import login 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.db.models import ProtectedError, Count
from django.db.models.functions import TruncDate
from django.utils import timezone


def inicio(request):
    """Página de inicio"""
    return render(request, "inicio.html")


def es_admin(user):
    """True si el usuario está autenticado y es staff"""
    return user.is_authenticated and user.is_staff


@user_passes_test(es_admin, login_url="tienda:login")
def panel_admin(request):
    """Dashboard admin — protegido para que solo entre el administrador"""
    # Ventas por día: agrupa los pedidos por fecha y los cuenta (últimos 7 días con ventas)
    ventas_por_dia = (
        Pedido.objects
        .annotate(dia=TruncDate("creado"))
        .values("dia")
        .annotate(cantidad=Count("id"))
        .order_by("-dia")[:7]
    )
    max_ventas = max([v["cantidad"] for v in ventas_por_dia], default=1)
    contexto = {
        "total_productos": Producto.objects.count(),
        "total_categorias": Categoria.objects.count(),
        "total_pedidos": Pedido.objects.count(),
        "pedidos_pendientes": Pedido.objects.filter(estado=Pedido.Estado.PENDIENTE).count(),
        "ventas_hoy": Pedido.objects.filter(creado__date=timezone.localdate()).count(),
        "ventas_por_dia": ventas_por_dia,
        "max_ventas": max_ventas,
        "ultimos_pedidos": Pedido.objects.select_related("usuario")[:5],
    }
    return render(request, "panel.html", contexto)


@user_passes_test(es_admin,login_url="tienda:login")
def admin_productos(request):
    """gestion de productos"""
    productos= Producto.objects.select_related("categoria")
    return render(request, "admin_productos.html", {"productos":productos}
                  )

@user_passes_test(es_admin,login_url="tienda:login")
def crear_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,"Producto creado correctamente")
            return redirect("tienda:admin_productos")
    else:
        form =ProductoForm()
    return render(request, "producto_form.html", { "form": form,"titulo":"Nuevo producto"})

@user_passes_test(es_admin,login_url="tienda:login")
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado.")
            return redirect("tienda:admin_productos")
    else:
        form = ProductoForm(instance=producto)
    return render(request,"producto_form.html",{"form": form,"titulo":"Editar producto"})


@user_passes_test(es_admin, login_url="tienda:login")
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        try:
            producto.delete()
            messages.success(request, "Producto eliminado.")
        except ProtectedError:
            messages.error(request, "No se puede eliminar: el producto está en pedidos.")
        return redirect("tienda:admin_productos")
    return render(request, "eliminar_producto.html", {"producto": producto})

def catalogo(request):
    productos = Producto.objects.filter(disponible=True).select_related("categoria")
    categorias = Categoria.objects.filter(activa=True)
    categoria_id = request.GET.get("categoria")
    if categoria_id and categoria_id.isdigit():
        productos = productos.filter(categoria_id=categoria_id)
    items, total = _items_carrito(request.session)
    return render(request, "catalogo.html", {
        "productos": productos,
        "categorias": categorias,
        "categoria_actual": categoria_id,
        "items": items,
        "total": total,
    })

def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, "detalle_producto.html", {"producto":producto})


def registro(request): 
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid(): 
            user = form.save()
            grupo, _ = Group.objects.get_or_create(name="Cliente")
            user.groups.add(grupo)
            login(request, user)
            messages.success(request, "¡Cuenta creada! Bienvenido/a")
            return redirect("tienda:inicio")
    else:
        form = UserCreationForm()
    return render(request, "registro.html", {"form": form})


def recuperar_password(request):
    """Recuperación simulada: cambia la contraseña validando usuario + formato de email."""
    if request.method == "POST":
        form = RecuperarPasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data["username"])
            user.set_password(form.cleaned_data["password1"])
            user.save()
            messages.success(request, "¡Contraseña actualizada! Ya podés iniciar sesión.")
            return redirect("tienda:login")
    else:
        form = RecuperarPasswordForm()
    return render(request, "recuperar_password.html", {"form": form})


def _items_carrito(session): 
    carrito= session.get("carrito", {})
    if not isinstance(carrito, dict):
        carrito = {}
    items, total= [], 0
    for pid, cantidad in carrito.items(): 
        if not str(pid).isdigit():
            continue
        producto = Producto.objects.filter(pk=pid, disponible=True).first()
        if not producto:
            continue
        subtotal = producto.precio * cantidad 
        total += subtotal 
        items.append({"producto": producto, "cantidad": cantidad, "subtotal": subtotal})
    return items, total
    
def ver_carrito(request):
    items, total = _items_carrito(request.session)
    return render(request,"carrito.html",{"items": items, "total": total})

MAX_POR_PRODUCTO = 20

def agregar_al_carrito(request,pk):
    producto =get_object_or_404(Producto, pk=pk)
    if not producto.disponible:
        messages.error(request, "Ese producto no está disponible.")
        return redirect(request.META.get("HTTP_REFERER") or "tienda:catalogo")
    carrito = request.session.get("carrito", {})
    clave= str(pk)
    if carrito.get(clave, 0) >= MAX_POR_PRODUCTO:
        messages.error(request, f"Máximo {MAX_POR_PRODUCTO} unidades por producto.")
        return redirect(request.META.get("HTTP_REFERER") or "tienda:catalogo")
    carrito[clave]= carrito.get(clave,0)+1
    request.session["carrito"] = carrito
    messages.success(request, f"{producto.nombre} agregado al carrito")
    return redirect(request.META.get("HTTP_REFERER") or "tienda:catalogo")

def quitar_del_carrito(request,pk  ):
    carrito = request.session.get("carrito", {})
    carrito.pop(str(pk), None)
    request.session["carrito"] = carrito
    return redirect(request.META.get("HTTP_REFERER") or "tienda:catalogo")

def checkout(request):
    items, total = _items_carrito(request.session)
    if not items: 
        messages.error(request, "tu carrito esta vacío")
        return redirect("tienda:catalogo")
    if request.method =="POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.usuario = request.user if request.user.is_authenticated else None
            modo = request.POST.get("modo_pago")
            pedido.modo_pago = modo if modo in Pedido.ModoPago.values else Pedido.ModoPago.LOCAL
            pedido.save()
            for item in items:
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=item["producto"],
                    cantidad=item["cantidad"],
                    precio_unitario=item["producto"].precio,

                )
            request.session["carrito"] = {}
            if pedido.modo_pago == Pedido.ModoPago.ONLINE:
                messages.success(request, f"¡Pago confirmado! Pedido #{pedido.id} pagado online. ✅")
            else:
                messages.success(request, f"¡Pedido #{pedido.id} reservado! Pagás al retirar. ☕")
            return redirect("tienda:mis_pedidos" if request.user.is_authenticated else "tienda:inicio")
    else:
        form = CheckoutForm()
    return render(request, "checkout.html", {"form": form, "items": items, "total": total})
    
@login_required(login_url="tienda:login")
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).prefetch_related("detalles__producto")
    return render(request, "mis_pedidos.html", {"pedidos":pedidos})

@user_passes_test(es_admin,login_url="tienda:login")
def admin_pedidos(request):
    pedidos = Pedido.objects.select_related("usuario").prefetch_related("detalles__producto")
    return render(request,"admin_pedidos.html", {"pedidos":pedidos,"estados":Pedido.Estado.choices})

@user_passes_test(es_admin,login_url="tienda:login")
def cambiar_estado_pedido(request,pk): 
    pedido=get_object_or_404(Pedido,pk=pk)
    if request.method=="POST": 
        nuevo = request.POST.get("estado")
        if nuevo in Pedido.Estado.values:
            pedido.estado=nuevo
            pedido.save()
            messages.success(request,f"Pedido #{pedido.id} actualizado")
    return redirect("tienda:admin_pedidos")

@user_passes_test(es_admin, login_url="tienda:login")
def admin_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, "admin_categorias.html", {"categorias": categorias})


@user_passes_test(es_admin, login_url="tienda:login")
def crear_categoria(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría creada.")
            return redirect("tienda:admin_categorias")
    else:
        form = CategoriaForm()
    return render(request, "categoria_form.html", {"form": form, "titulo": "Nueva categoría"})

@user_passes_test(es_admin, login_url="tienda:login")
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request,"Categoria actualizada.")
            return redirect("tienda:admin_categorias")
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, "categoria_form.html", {"form":form, "titulo":"Editar categoría"})


@user_passes_test(es_admin, login_url="tienda:login")
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
            try:
                categoria.delete()
                messages.success(request,"Categoría eliminada")
            except ProtectedError:
                messages.error(request, "No se puede eliminar: categoria tiene productos")
            return redirect("tienda:admin_categorias")
    return render(request, "eliminar_categoria.html", {"categoria":categoria})


@user_passes_test(es_admin, login_url="tienda:login")
def admin_usuarios(request):
    usuarios = User.objects.annotate(num_pedidos=Count("pedidos")).order_by("-date_joined")
    return render(request, "admin_usuarios.html", {"usuarios": usuarios})


@user_passes_test(es_admin, login_url="tienda:login")
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user:
        messages.error(request, "No podés eliminar tu propia cuenta.")
        return redirect("tienda:admin_usuarios")
    if usuario.is_superuser:
        messages.error(request, "No se puede eliminar a un superusuario.")
        return redirect("tienda:admin_usuarios")
    if request.method == "POST":
        nombre = usuario.username
        usuario.delete()
        messages.success(request, f"Usuario «{nombre}» eliminado. Sus pedidos quedan como Invitado.")
        return redirect("tienda:admin_usuarios")
    return render(request, "eliminar_usuario.html", {"usuario": usuario})