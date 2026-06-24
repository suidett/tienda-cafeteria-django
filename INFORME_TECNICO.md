# Informe Técnico — Vittorio Coffee

**Desarrollo de una tienda web para una cafetería de especialidad con el framework Django**

---

**Asignatura:** Diseño y Programación Orientada a la Web
**Carrera:** [Completar]
**Universidad:** Universidad Técnica Federico Santa María (UTFSM)
**Integrantes:** [Nombre 1], [Nombre 2], [Nombre 3]
**Profesor(a):** [Completar]
**Fecha:** Junio de 2026

---

## Resumen

El presente informe documenta el diseño y la implementación de **Vittorio Coffee**, una
tienda web para una cafetería de especialidad desarrollada con el framework **Django**.
El sistema permite a los clientes navegar un catálogo de productos, gestionar un carrito
de compras y confirmar pedidos —ya sea como usuarios registrados o como invitados— e
incorpora un panel de administración propio para la gestión de productos, categorías,
pedidos y usuarios. El desarrollo siguió el patrón arquitectónico **Modelo-Vista-Template
(MVT)** y empleó el **ORM** de Django para la persistencia en una base de datos SQLite.
Se incorporaron, además, validaciones y mecanismos de robustez para garantizar la
integridad de los datos y una experiencia de uso confiable.

**Palabras clave:** Django, desarrollo web, MVT, ORM, comercio electrónico, Python.

---

## 1. Introducción

El comercio electrónico se ha consolidado como un canal fundamental para los negocios
gastronómicos, permitiendo a los clientes realizar pedidos de manera autónoma y a los
locales optimizar su gestión. En este contexto, el presente trabajo aborda el desarrollo
de una aplicación web para una cafetería ficticia, *Vittorio Coffee*, que digitaliza el
proceso de venta: desde la exhibición de la carta hasta la confirmación del pedido y su
posterior gestión interna.

El proyecto se enmarca en la asignatura *Diseño y Programación Orientada a la Web* y tiene
como propósito aplicar los conceptos de desarrollo web del lado del servidor, el manejo de
bases de datos relacionales mediante un ORM, la autenticación de usuarios y el diseño de
interfaces.

## 2. Objetivos

### 2.1 Objetivo general
Desarrollar una aplicación web funcional para la gestión de ventas de una cafetería,
aplicando el framework Django y buenas prácticas de desarrollo web.

### 2.2 Objetivos específicos
- Modelar el dominio del negocio (productos, categorías, pedidos) mediante el ORM de Django.
- Implementar un catálogo público con carrito de compras y proceso de checkout.
- Desarrollar un sistema de autenticación con roles diferenciados (cliente y administrador).
- Construir un panel de administración propio para la gestión del negocio.
- Incorporar validaciones y mecanismos que aseguren la integridad y robustez del sistema.

## 3. Marco teórico

**Django** es un framework de desarrollo web de alto nivel escrito en Python, que promueve
el desarrollo rápido y un diseño limpio y pragmático. Se basa en el patrón
**Modelo-Vista-Template (MVT)**, una variante del clásico MVC:

- **Modelo (Model):** define la estructura de los datos y se mapea a tablas de la base de
  datos a través del **ORM** (Object-Relational Mapping), que permite manipular registros
  como objetos de Python sin escribir SQL directamente.
- **Vista (View):** contiene la lógica de negocio; recibe la petición HTTP, procesa los
  datos y decide qué respuesta entregar.
- **Template:** define la presentación (HTML) que se envía al navegador.

El framework incorpora de fábrica un sistema de autenticación, protección contra
vulnerabilidades comunes (CSRF, inyección SQL, XSS) y un sistema de migraciones para
versionar los cambios del esquema de la base de datos.

## 4. Metodología y herramientas

El desarrollo se organizó de manera **modular e incremental**, construyendo y verificando
una funcionalidad a la vez. Las herramientas utilizadas fueron:

| Herramienta | Uso |
|-------------|-----|
| Python 3.14 | Lenguaje de programación |
| Django 6.0 | Framework web |
| SQLite | Motor de base de datos |
| Pillow | Procesamiento de imágenes de productos |
| Bootstrap 5 + CSS propio | Diseño de la interfaz |
| JavaScript | Interactividad del lado del cliente |
| Git / GitHub | Control de versiones |

## 5. Desarrollo

### 5.1 Arquitectura
El proyecto se divide en el paquete de configuración `cafeteria/` (settings y URLs raíz) y
la aplicación `tienda/`, que concentra la lógica del negocio (modelos, vistas, formularios,
URLs y plantillas).

### 5.2 Modelo de datos
Se definieron cuatro entidades principales:

- **Categoria:** agrupa los productos (p. ej. *Cafés calientes*, *Postres*).
- **Producto:** ítem a la venta, asociado a una categoría (relación uno a muchos).
- **Pedido:** una compra confirmada, vinculada opcionalmente a un usuario (los invitados
  generan pedidos con usuario nulo). Registra estado, modo de pago y horario de retiro.
- **DetallePedido:** cada línea de un pedido (cantidad de un producto). Almacena el
  **precio unitario al momento de la compra**, de modo que el historial no se altera si
  posteriormente cambia el precio del producto.

Las relaciones emplean `on_delete=PROTECT` donde corresponde, para preservar la integridad
referencial y el historial de ventas.

### 5.3 Funcionalidades implementadas

**Para el cliente / público:**
- Catálogo con filtrado por categoría.
- Carrito de compras persistido en la sesión.
- Checkout con selección de horario de retiro (turnos generados dinámicamente) y modo de
  pago (pago en línea simulado o pago al retirar).
- Registro, inicio de sesión y recuperación de contraseña (simulada).
- Historial personal de pedidos.

**Para el administrador (panel protegido):**
- Tablero con estadísticas de ventas.
- CRUD completo de productos y categorías.
- Gestión del estado de los pedidos.
- Administración de usuarios.

### 5.4 Autenticación y roles
El sistema distingue dos roles: **cliente** (grupo asignado al registrarse) y
**administrador** (`is_staff`). El acceso al panel se restringe mediante el decorador
`@user_passes_test(es_admin)`, que redirige al login a cualquier usuario no autorizado.

## 6. Seguridad y validaciones

Se incorporaron diversos mecanismos de robustez, validados mediante pruebas adversariales:

- **Tope de cantidad** por producto en el carrito.
- Imposibilidad de agregar **productos no disponibles**.
- **Validación de precio** (valor mínimo) y de **teléfono** (formato).
- **Saneamiento de parámetros** de URL y de la sesión, evitando errores ante datos
  malformados (p. ej. `?categoria=abc`).
- **Prevención de pedidos duplicados** ante el doble envío del formulario.
- Manejo de `ProtectedError` al intentar eliminar registros referenciados por pedidos.
- Activación de **WAL (Write-Ahead Logging)** en SQLite para mejorar la concurrencia.

Adicionalmente, Django provee de forma nativa protección contra CSRF, inyección SQL (vía
ORM) y XSS (autoescape de plantillas), verificadas durante las pruebas.

## 7. Pruebas y verificación

El sistema se validó con el cliente de pruebas de Django (`Client`), comprobando el flujo
completo: navegación pública, registro e inicio de sesión, creación de pedidos, acceso al
panel y control de acceso por rol. Se ejecutaron, además, pruebas adversariales orientadas
a romper el sistema (inyección, manipulación de URLs y de la sesión, accesos no
autorizados), confirmando que las validaciones implementadas responden correctamente.

## 8. Conclusiones

El proyecto cumplió con los objetivos planteados, resultando en una aplicación web
funcional y robusta que digitaliza el proceso de venta de una cafetería. El uso de Django
permitió un desarrollo ordenado gracias a su arquitectura MVT, su ORM y sus utilidades
integradas de seguridad y autenticación. El trabajo permitió afianzar conocimientos sobre
el desarrollo web del lado del servidor, el modelado de datos relacionales y la importancia
de validar las entradas para construir sistemas confiables.

Como trabajo futuro, se proponen mejoras como la integración de una pasarela de pago real,
la gestión de inventario (stock) y el envío de notificaciones por correo electrónico.

## 9. Referencias

- Django Software Foundation. (2024). *Django documentation*. https://docs.djangoproject.com/
- Python Software Foundation. (2024). *Python documentation*. https://docs.python.org/3/
- The Bootstrap Team. (2024). *Bootstrap documentation*. https://getbootstrap.com/docs/
- Mozilla. (2024). *MDN Web Docs*. https://developer.mozilla.org/

---

> *Nota: este informe está en formato Markdown. Para la entrega en PDF con formato APA
> estricto (portada, interlineado doble, sangrías), se puede exportar a Word y ajustar el
> estilo, o pedir que se genere el documento `.docx` ya formateado.*
