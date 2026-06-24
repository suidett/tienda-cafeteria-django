# ☕ Vittorio Coffee — Tienda web (Django)

Tienda web de una cafetería de especialidad, desarrollada en **Django** para el ramo
*Diseño y Programación Orientada a la Web* (UTFSM). Los clientes pueden navegar la
carta, armar un pedido y comprarlo (registrados o como invitados); los administradores
gestionan productos, categorías, pedidos y usuarios desde un panel protegido.

## Tecnologías
- Python 3.14 · Django 6.0
- Base de datos: SQLite (con WAL activado para mejor concurrencia)
- Frontend: HTML semántico + CSS propio + Bootstrap 5 + JavaScript
- Pillow (manejo de imágenes de productos)

## Instalación y ejecución

```bash
# 1. Entrar a la carpeta del proyecto
cd DJANGO

# 2. Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Instalar las dependencias
pip install -r requirements.txt

# 4. Aplicar las migraciones (crea la base de datos y sus tablas)
python manage.py migrate

# 5. Levantar el servidor de desarrollo
python manage.py runserver

# 6. Abrir en el navegador:
#    http://localhost:8000/
```

> El proyecto incluye `db.sqlite3` con datos de demostración (productos, categorías y
> usuarios de prueba). Si querés partir de una base vacía: borrá `db.sqlite3`, corré
> `python manage.py migrate` y creá un admin con `python manage.py createsuperuser`.

## Credenciales de prueba

| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador (staff) | `admin` | `Cafe2024Admin` |
| Cliente | `cliente` | `Cafe2024Cliente` |

- El **administrador** accede al panel en `/panel/`.
- El **cliente** compra y ve su historial en *Mis pedidos*.
- También se puede **comprar como invitado**, sin registrarse.

## Roles y control de acceso
- **Cliente**: usuario registrado (grupo *Cliente*). Compra y ve sus pedidos.
- **Administrador**: usuario `is_staff`. Único que entra al panel (`/panel/...`),
  protegido con `@user_passes_test(es_admin)`. Un cliente o un anónimo que intente
  entrar es redirigido al login.
- La compra es pública (invitado o cliente); la gestión es exclusiva del administrador.

## Funcionalidades

**Público / cliente**
- Página de inicio con la identidad de la cafetería.
- Carta (catálogo) con filtro por categoría.
- Carrito en sesión (agregar / quitar) visible al lado de la carta.
- Checkout que **crea el pedido en la base de datos** (como cliente o invitado), con
  **horario de retiro** (turnos dinámicos cada 30 min) y **modo de pago** (online
  simulado con Mercado Pago, o pago al retirar).
- *Mis pedidos*: historial del cliente logueado, con estado y datos del pedido.
- Registro, login y **recuperación de contraseña** (simulada).

**Administrador (panel protegido)**
- Dashboard con estadísticas y gráfico de ventas por día.
- CRUD de productos y de categorías.
- Gestión de pedidos: cambiar estado (pendiente → en preparación → listo → entregado → cancelado).
- **Gestión de usuarios**: listado y eliminación (con protecciones: no auto-eliminación, no superusuarios).

## Validaciones y robustez
- **Tope de cantidad** por producto en el carrito (evita pedidos absurdos).
- No se pueden agregar al carrito **productos no disponibles**.
- **Precio mínimo** en productos (`MinValueValidator`), evita precios 0 o negativos.
- **Teléfono validado** en el checkout (mínimo de dígitos).
- **Filtros y carrito a prueba de datos corruptos** (un `?categoria=abc` o una sesión
  con datos raros no rompen el sitio).
- **Anti-doble-pedido**: el botón de compra se bloquea tras el primer envío.
- Borrar un producto o categoría que está en pedidos no rompe (se maneja `ProtectedError`).
- SQLite con **WAL + timeout** para soportar varias escrituras concurrentes.

## Estructura del proyecto
```
DJANGO/
├── cafeteria/          # configuración del proyecto (settings, urls raíz)
├── tienda/             # app principal
│   ├── models.py       # Categoria, Producto, Pedido, DetallePedido
│   ├── views.py        # vistas (público, cliente, admin)
│   ├── urls.py         # rutas de la app
│   ├── forms.py        # ProductoForm, CategoriaForm, CheckoutForm, RecuperarPasswordForm
│   ├── admin.py        # registro en el admin de Django
│   └── templates/      # plantillas HTML
├── static/             # CSS, JS e imágenes (logo)
├── media/              # imágenes subidas (productos)
├── db.sqlite3          # base de datos
├── requirements.txt    # dependencias
└── manage.py
```

## Modelo de datos (resumen)
- **Categoria** 1—N **Producto**
- **User** 1—N **Pedido** (un pedido puede ser de un invitado → usuario nulo)
- **Pedido** 1—N **DetallePedido** — y cada **DetallePedido** apunta a un **Producto**
- `DetallePedido` guarda el `precio_unitario` al momento de la compra, para que el
  historial no cambie si después se modifica el precio del producto.

## Documentación adicional
- **GUIA.md** — mapa "quiero cambiar X → tocá este archivo".
- **DEFENSA.md** — preguntas probables de la defensa con el código exacto del cambio.
- **COMANDOS.md** — comandos de Django y Git del día a día.
- **INFORME_TECNICO.md** — documento técnico del proyecto (estructura APA).
