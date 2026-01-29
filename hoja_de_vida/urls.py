from http import server
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings  # <--- AÑADE ESTO
from django.conf.urls.static import static # <--- AÑADE ESTO
from django.views.static import serve
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('curriculum.urls')),
]

# ESTO ES LO QUE FALTA PARA QUE LA IMAGEN SE MUESTRE:
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Cambia "server" por "serve"
urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})]