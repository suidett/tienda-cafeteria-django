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
    return render(request, "inicio.html")  # solo muestra la portada


def es_admin(user):
    """True si el usuario está autenticado y es staff"""
    # esta función se usa para proteger las páginas del panel
    return user.is_authenticated and user.is_staff


@user_passes_test(es_admin, login_url="tienda:login")  # 🔒 solo entra el admin
def panel_admin(request):
    """Dashboard admin — protegido para que solo entre el administrador"""
    # Ventas por día: agrupa los pedidos por fecha y los cuenta (últimos 7 días con ventas)
    ventas_por_dia = (
        Pedido.objects
        .annotate(dia=TruncDate("creado"))   # agrupa por día
        .values("dia")
        .annotate(cantidad=Count("id"))      # cuenta cuántos pedidos por día
        .order_by("-dia")[:7]                # los últimos 7
    )
    max_ventas = max([v["cantidad"] for v in ventas_por_dia], default=1)  # el día con más ventas (para el gráfico)
    # diccionario con todos los datos que se mandan al template del panel
    contexto = {
        "total_productos": Producto.objects.count(),     # cantidad de productos
        "total_categorias": Categoria.objects.count(),   # cantidad de categorías
        "total_pedidos": Pedido.objects.count(),         # cantidad de pedidos
        "pedidos_pendientes": Pedido.objects.filter(estado=Pedido.Estado.PENDIENTE).count(),  # pedidos sin entregar
        "ventas_hoy": Pedido.objects.filter(creado__date=timezone.localdate()).count(),       # pedidos de hoy
        "ventas_por_dia": ventas_por_dia,
        "max_ventas": max_ventas,
        "ultimos_pedidos": Pedido.objects.select_related("usuario")[:5],  # últimos 5 pedidos
    }
    return render(request, "panel.html", contexto)


@user_passes_test(es_admin,login_url="tienda:login")  # 🔒 solo admin
def admin_productos(request):
    """gestion de productos"""
    productos= Producto.objects.select_related("categoria")  # trae todos los productos con su categoría
    return render(request, "admin_productos.html", {"productos":productos}
                  )

@user_passes_test(es_admin,login_url="tienda:login")  # 🔒 solo admin
def crear_producto(request):
    if request.method == "POST":  # si el admin envió el formulario
        form = ProductoForm(request.POST, request.FILES)  # FILES = por la imagen
        if form.is_valid():       # si los datos son válidos
            form.save()           # lo guarda en la base
            messages.success(request,"Producto creado correctamente")  # mensaje verde
            return redirect("tienda:admin_productos")  # vuelve a la lista
    else:  # primera vez que entra (todavía no envió nada)
        form =ProductoForm()  # formulario vacío
    return render(request, "producto_form.html", { "form": form,"titulo":"Nuevo producto"})

@user_passes_test(es_admin,login_url="tienda:login")  # 🔒 solo admin
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)  # busca el producto por su id (o error 404)
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)  # instance = edita el existente
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado.")
            return redirect("tienda:admin_productos")
    else:
        form = ProductoForm(instance=producto)  # carga el formulario con los datos actuales
    return render(request,"producto_form.html",{"form": form,"titulo":"Editar producto"})


@user_passes_test(es_admin, login_url="tienda:login")  # 🔒 solo admin
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)  # busca el producto
    if request.method == "POST":  # confirmó el borrado
        try:
            producto.delete()  # lo borra
            messages.success(request, "Producto eliminado.")
        except ProtectedError:  # si el producto está en pedidos, no se puede borrar
            messages.error(request, "No se puede eliminar: el producto está en pedidos.")
        return redirect("tienda:admin_productos")
    return render(request, "eliminar_producto.html", {"producto": producto})  # pantalla de confirmación

def catalogo(request):
    productos = Producto.objects.filter(disponible=True).select_related("categoria")  # solo los disponibles
    categorias = Categoria.objects.filter(activa=True)  # solo las categorías activas
    categoria_id = request.GET.get("categoria")  # lee ?categoria=X de la URL (el filtro)
    if categoria_id and categoria_id.isdigit():  # isdigit() = chequea que sea un número (seguridad)
        productos = productos.filter(categoria_id=categoria_id)  # filtra por esa categoría
    items, total = _items_carrito(request.session)  # arma el resumen del carrito
    return render(request, "catalogo.html", {
        "productos": productos,
        "categorias": categorias,
        "categoria_actual": categoria_id,
        "items": items,
        "total": total,
    })

def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)  # busca el producto por id
    return render(request, "detalle_producto.html", {"producto":producto})


def registro(request):
    if request.method == "POST":  # envió el formulario de registro
        form = UserCreationForm(request.POST)  # formulario de usuario que trae Django
        if form.is_valid():
            user = form.save()  # crea el usuario
            grupo, _ = Group.objects.get_or_create(name="Cliente")  # grupo "Cliente"
            user.groups.add(grupo)  # lo agrega al grupo
            login(request, user)  # lo deja logueado automáticamente
            messages.success(request, "¡Cuenta creada! Bienvenido/a")
            return redirect("tienda:inicio")
    else:
        form = UserCreationForm()  # formulario vacío
    return render(request, "registro.html", {"form": form})


def recuperar_password(request):
    """Recuperación simulada: cambia la contraseña validando usuario + formato de email."""
    if request.method == "POST":
        form = RecuperarPasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data["username"])  # busca el usuario
            user.set_password(form.cleaned_data["password1"])  # set_password encripta la nueva clave
            user.save()
            messages.success(request, "¡Contraseña actualizada! Ya podés iniciar sesión.")
            return redirect("tienda:login")
    else:
        form = RecuperarPasswordForm()
    return render(request, "recuperar_password.html", {"form": form})


def _items_carrito(session):
    # función ayudante: arma la lista de productos del carrito y calcula el total
    carrito= session.get("carrito", {})  # el carrito vive en la sesión (un diccionario {id: cantidad})
    if not isinstance(carrito, dict):  # seguridad: si el carrito no es un diccionario, lo vacía
        carrito = {}
    items, total= [], 0
    for pid, cantidad in carrito.items():  # recorre cada producto del carrito
        if not str(pid).isdigit():  # seguridad: ignora ids que no sean números
            continue
        producto = Producto.objects.filter(pk=pid, disponible=True).first()  # busca el producto
        if not producto:  # si no existe o no está disponible, lo saltea
            continue
        subtotal = producto.precio * cantidad
        total += subtotal
        items.append({"producto": producto, "cantidad": cantidad, "subtotal": subtotal})
    return items, total

def ver_carrito(request):
    items, total = _items_carrito(request.session)  # arma el carrito
    return render(request,"carrito.html",{"items": items, "total": total})

MAX_POR_PRODUCTO = 20  # tope de unidades por producto en el carrito

def agregar_al_carrito(request,pk):
    producto =get_object_or_404(Producto, pk=pk)  # busca el producto
    if not producto.disponible:  # si no está disponible, no lo deja agregar
        messages.error(request, "Ese producto no está disponible.")
        return redirect(request.META.get("HTTP_REFERER") or "tienda:catalogo")  # vuelve a donde estaba
    carrito = request.session.get("carrito", {})  # toma el carrito de la sesión
    clave= str(pk)
    if carrito.get(clave, 0) >= MAX_POR_PRODUCTO:  # si ya llegó al tope
        messages.error(request, f"Máximo {MAX_POR_PRODUCTO} unidades por producto.")
        return redirect(request.META.get("HTTP_REFERER") or "tienda:catalogo")
    carrito[clave]= carrito.get(clave,0)+1  # suma 1 unidad
    request.session["carrito"] = carrito  # guarda el carrito en la sesión
    messages.success(request, f"{producto.nombre} agregado al carrito")
    return redirect(request.META.get("HTTP_REFERER") or "tienda:catalogo")

def quitar_del_carrito(request,pk  ):
    carrito = request.session.get("carrito", {})
    carrito.pop(str(pk), None)  # saca ese producto del carrito
    request.session["carrito"] = carrito
    return redirect(request.META.get("HTTP_REFERER") or "tienda:catalogo")

def checkout(request):
    items, total = _items_carrito(request.session)  # arma el carrito
    if not items:  # si el carrito está vacío, no deja seguir
        messages.error(request, "tu carrito esta vacío")
        return redirect("tienda:catalogo")
    if request.method =="POST":  # envió el formulario de compra
        form = CheckoutForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)  # arma el pedido pero todavía NO lo guarda
            pedido.usuario = request.user if request.user.is_authenticated else None  # si no está logueado: queda como invitado
            modo = request.POST.get("modo_pago")
            pedido.modo_pago = modo if modo in Pedido.ModoPago.values else Pedido.ModoPago.LOCAL  # seguridad: solo modos de pago válidos
            pedido.save()  # ahora sí guarda el pedido
            for item in items:  # crea una línea de detalle por cada producto del carrito
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=item["producto"],
                    cantidad=item["cantidad"],
                    precio_unitario=item["producto"].precio,  # guarda el precio de AHORA (historial fijo)

                )
            request.session["carrito"] = {}  # vacía el carrito
            if pedido.modo_pago == Pedido.ModoPago.ONLINE:
                messages.success(request, f"¡Pago confirmado! Pedido #{pedido.id} pagado online. ✅")
            else:
                messages.success(request, f"¡Pedido #{pedido.id} reservado! Pagás al retirar. ☕")
            return redirect("tienda:mis_pedidos" if request.user.is_authenticated else "tienda:inicio")
    else:
        form = CheckoutForm()  # formulario vacío
    return render(request, "checkout.html", {"form": form, "items": items, "total": total})

@login_required(login_url="tienda:login")  # 🔒 hay que estar logueado
def mis_pedidos(request):
    # trae solo los pedidos del usuario logueado
    pedidos = Pedido.objects.filter(usuario=request.user).prefetch_related("detalles__producto")
    return render(request, "mis_pedidos.html", {"pedidos":pedidos})

@user_passes_test(es_admin,login_url="tienda:login")  # 🔒 solo admin
def admin_pedidos(request):
    # trae TODOS los pedidos (con su usuario y sus detalles) para el panel
    pedidos = Pedido.objects.select_related("usuario").prefetch_related("detalles__producto")
    return render(request,"admin_pedidos.html", {"pedidos":pedidos,"estados":Pedido.Estado.choices})

@user_passes_test(es_admin,login_url="tienda:login")  # 🔒 solo admin
def cambiar_estado_pedido(request,pk):
    pedido=get_object_or_404(Pedido,pk=pk)  # busca el pedido
    if request.method=="POST":
        nuevo = request.POST.get("estado")
        if nuevo in Pedido.Estado.values:  # seguridad: solo estados válidos
            pedido.estado=nuevo  # cambia el estado (ej: pendiente → entregado)
            pedido.save()
            messages.success(request,f"Pedido #{pedido.id} actualizado")
    return redirect("tienda:admin_pedidos")

@user_passes_test(es_admin, login_url="tienda:login")  # 🔒 solo admin
def admin_categorias(request):
    categorias = Categoria.objects.all()  # todas las categorías
    return render(request, "admin_categorias.html", {"categorias": categorias})


@user_passes_test(es_admin, login_url="tienda:login")  # 🔒 solo admin
def crear_categoria(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()  # guarda la categoría nueva
            messages.success(request, "Categoría creada.")
            return redirect("tienda:admin_categorias")
    else:
        form = CategoriaForm()
    return render(request, "categoria_form.html", {"form": form, "titulo": "Nueva categoría"})

@user_passes_test(es_admin, login_url="tienda:login")  # 🔒 solo admin
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)  # busca la categoría
    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)  # edita la existente
        if form.is_valid():
            form.save()
            messages.success(request,"Categoria actualizada.")
            return redirect("tienda:admin_categorias")
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, "categoria_form.html", {"form":form, "titulo":"Editar categoría"})


@user_passes_test(es_admin, login_url="tienda:login")  # 🔒 solo admin
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
            try:
                categoria.delete()  # la borra
                messages.success(request,"Categoría eliminada")
            except ProtectedError:  # no se puede si tiene productos
                messages.error(request, "No se puede eliminar: categoria tiene productos")
            return redirect("tienda:admin_categorias")
    return render(request, "eliminar_categoria.html", {"categoria":categoria})  # confirmación


@user_passes_test(es_admin, login_url="tienda:login")  # 🔒 solo admin
def admin_usuarios(request):
    # lista los usuarios y cuenta cuántos pedidos hizo cada uno
    usuarios = User.objects.annotate(num_pedidos=Count("pedidos")).order_by("-date_joined")
    return render(request, "admin_usuarios.html", {"usuarios": usuarios})


@user_passes_test(es_admin, login_url="tienda:login")  # 🔒 solo admin
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user:  # no podés borrarte a vos mismo
        messages.error(request, "No podés eliminar tu propia cuenta.")
        return redirect("tienda:admin_usuarios")
    if usuario.is_superuser:  # no se puede borrar a un superusuario
        messages.error(request, "No se puede eliminar a un superusuario.")
        return redirect("tienda:admin_usuarios")
    if request.method == "POST":
        nombre = usuario.username
        usuario.delete()  # borra el usuario (sus pedidos quedan como Invitado por el SET_NULL)
        messages.success(request, f"Usuario «{nombre}» eliminado. Sus pedidos quedan como Invitado.")
        return redirect("tienda:admin_usuarios")
    return render(request, "eliminar_usuario.html", {"usuario": usuario})  # confirmación
