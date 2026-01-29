from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('perfil/', views.perfil, name='perfil'),
    path('experiencia/', views.experiencia, name='experiencia'),
    path('educacion/', views.educacion, name='educacion'),
    path('cursos/', views.cursos, name='cursos'),
    path('reconocimientos/', views.reconocimientos, name='reconocimientos'),
    path('trabajos/', views.trabajos, name='trabajos'),
    path('venta/', views.venta, name='venta'),
    path('contacto/', views.contacto, name='contacto'),
    # Esta es la ruta que faltaba y causaba el error
    path('generar-cv/', views.generar_cv, name='generar_cv'),
]