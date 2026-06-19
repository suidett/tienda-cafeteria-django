"""
Rutas raíz del proyecto cafeteria.
Acá "enchufamos" las rutas de cada app y, en desarrollo, servimos las imágenes subidas.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),     # panel admin que trae Django
    path("", include("tienda.urls")),    # todas las rutas de nuestra app tienda
]

# En desarrollo (DEBUG=True) Django sirve los archivos "media" (imágenes de productos).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
