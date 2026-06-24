# 🗺️ Guía de desarrollo — Vittorio Coffee

Mapa rápido de **dónde está cada parte del código** y **qué archivo tocar** para cada cambio típico. Para ubicarte sin leer todo el proyecto.

---

## 1. Mapa del proyecto

```
DJANGO/
├── manage.py                   ← comandos de Django (runserver, migrate…)
├── requirements.txt            ← dependencias
├── db.sqlite3                  ← base de datos (con datos de prueba)
│
├── cafeteria/                  ← CONFIGURACIÓN del proyecto
│   ├── settings.py             ← idioma, base de datos, apps, login, estáticos
│   └── urls.py                 ← rutas raíz (incluye las de la app `tienda`)
│
├── tienda/                     ← LA APLICACIÓN (todo lo importante)
│   ├── models.py               ← las TABLAS (Categoria, Producto, Pedido, DetallePedido)
│   ├── views.py                ← la LÓGICA (qué hace cada página)
│   ├── urls.py                 ← las RUTAS (qué URL llama a qué vista)
│   ├── forms.py                ← los FORMULARIOS (producto, categoría, checkout, recuperar)
│   ├── admin.py                ← el /admin de Django
│   ├── migrations/             ← historial de cambios de la base
│   └── templates/              ← los HTML (lo que se ve)
│
├── static/                     ← CSS, JS e imágenes
│   ├── css/estilos.css
│   ├── js/validaciones.js
│   └── img/
└── media/                      ← imágenes subidas (fotos de productos)
```

**El flujo de Django:**
> El usuario entra a una URL → `urls.py` elige la función de `views.py` → esa función
> consulta `models.py` (la base) y arma datos → se los pasa a un `template` (HTML) → se muestra.

---

## 2. "Quiero cambiar… ¿dónde lo toco?"

### 🎨 Los colores / el diseño
`static/css/estilos.css` → en el bloque `:root` están las variables (`--accent`, etc.).
Cambialas y cambia todo el sitio.
> ⚠️ Tras editar el CSS, subí el cache-buster en `tienda/templates/base.html`
> (`?v=10` → `?v=11`) para que el navegador no use el caché viejo.

### 🧱 El encabezado, el menú y el pie de página
`tienda/templates/base.html` — es la plantilla "madre" de todas las páginas.

### 🏠 La página de inicio
- HTML: `tienda/templates/inicio.html`
- Lógica: función `inicio()` en `tienda/views.py`

### 📋 La carta / catálogo
- HTML: `tienda/templates/catalogo.html`
- Lógica (qué productos trae, filtro por categoría): función `catalogo()` en `tienda/views.py`

### ☕ Los productos, precios y categorías (los datos)
1. **Desde el panel (lo más fácil):** entrá como `admin` → `/panel/` → Productos / Categorías.
2. **Desde el código:** la estructura de las tablas está en `tienda/models.py`.

### 🛒 El carrito (agregar / quitar / tope de cantidad)
`tienda/views.py`: funciones `_items_carrito`, `agregar_al_carrito`, `quitar_del_carrito`.
El tope por producto es la constante `MAX_POR_PRODUCTO` (en `views.py`).

### ✅ El checkout (qué pide y qué guarda)
- Campos del formulario: `CheckoutForm` en `tienda/forms.py`
- Qué hace al comprar (crea el pedido): función `checkout()` en `tienda/views.py`
- HTML: `tienda/templates/checkout.html`
- Los **horarios de retiro** se arman en `forms.py`, función `generar_slots_retiro()`
  (parámetros arriba: hora de apertura/cierre, paso en minutos…).

### 🛠️ El panel de administración
- Lógica: `tienda/views.py` (`panel_admin`, `admin_productos`, `crear/editar/eliminar_producto`,
  `admin_categorias`, `admin_pedidos`, `cambiar_estado_pedido`, `admin_usuarios`…)
- HTML: `panel.html`, `admin_productos.html`, `admin_pedidos.html`, `admin_usuarios.html`, etc.

### 👤 Login / registro / recuperar contraseña
- Vistas: `registro`, `recuperar_password` en `tienda/views.py`
- HTML: `login.html`, `registro.html`, `recuperar_password.html`

---

## 3. Tareas frecuentes

### Agregar un campo nuevo a una tabla (ej. "stock")
1. Editá la clase en `tienda/models.py`.
2. Corré: `python manage.py makemigrations` y `python manage.py migrate`.

### Agregar una página nueva
1. Escribí la función en `tienda/views.py`.
2. Agregá la ruta en `tienda/urls.py`.
3. Creá el HTML en `tienda/templates/` (con `{% extends 'base.html' %}`).

> 💡 Para respuestas con el **código exacto** de cada cambio típico, mirá **DEFENSA.md**.

---

## 4. Comandos útiles
```bash
python manage.py runserver        # levantar el sitio
python manage.py makemigrations   # detectar cambios en los modelos
python manage.py migrate          # aplicar esos cambios a la base
python manage.py createsuperuser  # crear un administrador
python manage.py check            # revisar que no haya errores
```

## 5. Las tablas (modelos)
| Modelo | Para qué sirve |
|--------|----------------|
| `Categoria` | Agrupa los productos (Cafés calientes, Postres…) |
| `Producto` | Lo que se vende (nombre, precio, categoría, foto, disponible) |
| `Pedido` | Un pedido confirmado (usuario o invitado, estado, total, retiro/pago) |
| `DetallePedido` | Cada línea del pedido (cantidad × producto, con el precio del momento) |

> **Regla de oro:** si dudás dónde tocar, pensá en 3 capas → **dato** (`models.py`) ·
> **lógica** (`views.py`) · **diseño** (template / `estilos.css`).
