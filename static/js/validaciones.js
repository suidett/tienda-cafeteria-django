// ============================================================
//  JavaScript de la cafetería
// ============================================================

// --- Menú hamburguesa (estilo Vittorio): abre/cierra el overlay ---
document.addEventListener("DOMContentLoaded", function () {
    const menuBtn = document.querySelector("[data-menu-btn]");
    const menu = document.querySelector("[data-menu]");
    const menuClose = document.querySelector("[data-menu-close]");
    const menuLinks = document.querySelectorAll("[data-menu-link]");

    function abrirMenu() {
        menu.classList.add("is-open");
        menuBtn.setAttribute("aria-expanded", "true");
        document.body.style.overflow = "hidden";   // bloquea el scroll de fondo
    }
    function cerrarMenu() {
        menu.classList.remove("is-open");
        menuBtn.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
    }

    if (menuBtn && menu) {
        menuBtn.addEventListener("click", abrirMenu);
        if (menuClose) menuClose.addEventListener("click", cerrarMenu);
        menuLinks.forEach(function (link) {
            link.addEventListener("click", cerrarMenu);
        });
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape") cerrarMenu();
        });
    }
});

// --- Validación simple de formularios: marca en rojo los campos requeridos vacíos ---
document.addEventListener("DOMContentLoaded", function () {
    const forms = document.querySelectorAll("form.form-render");
    forms.forEach(function (form) {
        form.addEventListener("submit", function (e) {
            let hayError = false;
            form.querySelectorAll("[required]").forEach(function (campo) {
                if (!campo.value.trim()) {
                    campo.style.border = "1px solid #c4623a";
                    hayError = true;
                } else {
                    campo.style.border = "";
                }
            });
            if (hayError) e.preventDefault();   // no envía si falta algo
        });
    });
});
