from django.contrib import admin
from django.utils.html import format_html
from .models import (
    DatosPersonales, 
    ExperienciaLaboral, 
    EstudioRealizado, 
    CursoCapacitacion, 
    Reconocimiento, 
    ProductoLaboral, 
    VentaGarage
)

# Configuración del encabezado del panel (Opcional, pero se ve pro)
admin.site.site_header = "Administración de Portafolio - Israel"
admin.site.index_title = "Panel de Control"
admin.site.site_title = "Admin Israel"

@admin.register(DatosPersonales)
class DatosPersonalesAdmin(admin.ModelAdmin):
    # Mostramos columnas clave en la lista
    list_display = ('nombres', 'apellidos', 'email', 'telefono', 'mostrar_telefono')
    
    # Esto permite editar el switch de privacidad directamente desde la lista
    list_editable = ('mostrar_telefono',)
    
    # Organizamos los campos en secciones (Fieldsets) para que se vea ordenado
    fieldsets = (
        ('Identidad', {
            'fields': ('nombres', 'apellidos', 'cedula', 'foto', 'descripcion_perfil')
        }),
        ('Información Demográfica', {
            'fields': ('fecha_nacimiento', 'sexo', 'estado_civil', 'nacionalidad', 'lugar_nacimiento')
        }),
        ('Contacto y Privacidad', {
            'fields': ('email', 'telefono', 'mostrar_telefono', 'telefono_convencional', 'sitio_web', 'direccion', 'mostrar_direccion_domiciliaria', 'direccion_trabajo')
        }),
        ('Redes Sociales', {
            'fields': ('url_linkedin', 'url_github', 'url_instagram')
        }),
        ('Legal', {
            'fields': ('licencia',)
        }),
    )

@admin.register(ExperienciaLaboral)
class ExperienciaLaboralAdmin(admin.ModelAdmin):
    list_display = ('cargo', 'empresa', 'fecha_inicio', 'fecha_fin', 'visible')
    list_filter = ('visible', 'empresa') # Barra lateral de filtros
    search_fields = ('cargo', 'empresa', 'descripcion') # Barra de búsqueda
    list_editable = ('visible',) # Switch rápido
    ordering = ('-fecha_inicio',)

@admin.register(EstudioRealizado)
class EstudioRealizadoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'institucion', 'fecha_inicio', 'fecha_fin', 'visible')
    list_filter = ('visible', 'institucion')
    search_fields = ('titulo', 'institucion')
    list_editable = ('visible',)

@admin.register(CursoCapacitacion)
class CursoCapacitacionAdmin(admin.ModelAdmin):
    # Agregamos 'ver_portada' y 'ver_certificado' a la lista
    list_display = ('nombre_curso', 'institucion', 'horas', 'fecha_realizacion', 'ver_portada', 'ver_certificado', 'visible')
    search_fields = ('nombre_curso', 'institucion')
    list_filter = ('fecha_realizacion',)
    list_editable = ('visible',)

    # Función para mostrar la miniatura de la imagen
    def ver_portada(self, obj):
        # Nota: Uso 'imagen_portada' porque así lo llamas en tu HTML. 
        # Si en tu models.py se llama diferente (ej: 'imagen'), cámbialo aquí.
        if hasattr(obj, 'imagen_portada') and obj.imagen_portada:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.imagen_portada.url
            )
        return "Sin imagen"
    
    ver_portada.short_description = "Portada"

    # Función para mostrar el botón del PDF
    def ver_certificado(self, obj):
        if obj.certificado_pdf:
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #5A7D84; color: white; padding: 4px 10px; border-radius: 5px; text-decoration: none; font-weight: bold;">Ver PDF</a>',
                obj.certificado_pdf.url
            )
        return "No hay PDF"
    
    ver_certificado.short_description = "Certificado"

@admin.register(Reconocimiento)
class ReconocimientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'institucion', 'fecha', 'visible')
    search_fields = ('nombre', 'institucion')
    list_editable = ('visible',)

@admin.register(ProductoLaboral)
class ProductoLaboralAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha', 'registro_id', 'visible')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('visible',)

@admin.register(VentaGarage)
class VentaGarageAdmin(admin.ModelAdmin):
    # Aquí es muy útil ver el stock y precio rápido
    list_display = ('nombre_producto', 'precio', 'estado', 'stock', 'activo')
    list_filter = ('estado', 'activo')
    search_fields = ('nombre_producto', 'item_id', 'descripcion')
    list_editable = ('precio', 'stock', 'activo') # Edita precios y stock sin entrar al producto
    list_per_page = 20