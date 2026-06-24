"""Rutas (URLs) de la app tienda."""
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

# Prefijo de nombres de esta app: permite escribir {% url 'tienda:inicio' %} en los templates.
app_name = "tienda"

urlpatterns = [
    path("", views.inicio, name="inicio"),

    # --- Autenticación (vistas que trae Django listas) ---
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("panel/", views.panel_admin, name="panel"),
    path("panel/productos/", views.admin_productos, name="admin_productos"),
    path("panel/productos/nuevo/", views.crear_producto, name="crear_producto"),
    path("panel/productos/<int:pk>/editar/", views.editar_producto, name="editar_producto"),
    path("panel/productos/<int:pk>/eliminar/", views.eliminar_producto, name="eliminar_producto"),
    path("catalogo/", views.catalogo, name="catalogo"),
    path("producto/<int:pk>/", views.detalle_producto, name="detalle_producto"),
    path("registro/", views.registro, name="registro"),
    path("recuperar/", views.recuperar_password, name="recuperar_password"),
    path("carrito/", views.ver_carrito, name="ver_carrito"),
    path("carrito/agregar/<int:pk>/", views.agregar_al_carrito, name="agregar_al_carrito"),
    path("carrito/quitar/<int:pk>/", views.quitar_del_carrito, name="quitar_del_carrito"),
    path("checkout/", views.checkout, name="checkout"),
    path("mis-pedidos/", views.mis_pedidos, name="mis_pedidos"),
    path("panel/pedidos/", views.admin_pedidos, name="admin_pedidos"),
    path("panel/pedidos/<int:pk>/estado/", views.cambiar_estado_pedido, name="cambiar_estado_pedido"),
    path("panel/categorias/", views.admin_categorias, name="admin_categorias"),
    path("panel/categorias/nueva/", views.crear_categoria, name="crear_categoria"),
    path("panel/categorias/<int:pk>/editar/", views.editar_categoria, name="editar_categoria"),
    path("panel/categorias/<int:pk>/eliminar/", views.eliminar_categoria, name="eliminar_categoria"),
    path("panel/usuarios/", views.admin_usuarios, name="admin_usuarios"),
    path("panel/usuarios/<int:pk>/eliminar/", views.eliminar_usuario, name="eliminar_usuario"),
]
