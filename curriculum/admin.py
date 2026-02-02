from django.contrib import admin
from django.utils.html import format_html
from .models import (
    DatosPersonales, 
    ExperienciaLaboral, 
    EstudioRealizado, 
    CursoCapacitacion,
    ProductoAcademico, 
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
    # ORGANIZACIÓN VISUAL (Fieldsets)
    fieldsets = (
        ('Información del Cargo', {
            'fields': ('cargo', 'empresa', 'ubicacion', 'fecha_inicio', 'fecha_fin', 'descripcion')
        }),
        ('Contacto Empresarial', {
            'fields': ('nombre_contacto', 'telefono_contacto', 'email_empresa', 'sitio_web_empresa')
        }),
        ('Archivos', {
            'fields': ('certificado', 'visible')
        }),
    )

@admin.register(EstudioRealizado)
class EstudioRealizadoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'institucion', 'fecha_inicio', 'fecha_fin', 'visible')
    list_filter = ('visible', 'institucion')
    search_fields = ('titulo', 'institucion')
    list_editable = ('visible',)
    # Organización Visual
    fieldsets = (
        ('Información Académica', {
            'fields': ('titulo', 'institucion', 'fecha_inicio', 'fecha_fin')
        }),
        ('Detalles Adicionales', {
            'fields': ('descripcion',)  # <--- Aquí aparece el nuevo campo
        }),
        ('Documentación', {
            'fields': ('archivo', 'visible')
        }),
    )

@admin.register(CursoCapacitacion)
class CursoCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('nombre_curso', 'institucion', 'horas', 'fecha_inicio', 'fecha_fin', 'visible')
    search_fields = ('nombre_curso', 'institucion')
    list_filter = ('fecha_fin', 'visible',)
    list_editable = ('visible',)
    # ORGANIZACIÓN VISUAL (Fieldsets)
    fieldsets = (
        ('Información Académica', {
            'fields': ('nombre_curso', 'institucion', 'horas', 'fecha_inicio', 'fecha_fin', 'descripcion')
        }),
        ('Contacto y Patrocinio', {
            'fields': ('nombre_contacto', 'telefono_contacto', 'email_empresa')
        }),
        ('Archivos', {
            'fields': ('certificado_pdf', 'visible')
        }),
    )

@admin.register(Reconocimiento)
class ReconocimientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'institucion', 'fecha', 'visible')
    search_fields = ('nombre', 'institucion')
    list_editable = ('visible',)
    # ORGANIZACIÓN VISUAL (Fieldsets)
    fieldsets = (
        ('Detalle del Reconocimiento', {
            'fields': ('nombre', 'institucion', 'fecha', 'codigo_registro', 'descripcion')
        }),
        ('Contacto Auspiciante', {
            'fields': ('nombre_contacto', 'telefono_contacto')
        }),
        ('Archivos', {
            'fields': ('certificado_pdf', 'visible')
        }),
    )
    

@admin.register(ProductoLaboral)
class ProductoLaboralAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha', 'visible')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('visible',)
    ordering = ('-fecha',)
    # Organización visual
    fieldsets = (
        ('Información del Proyecto', {
            'fields': ('nombre', 'fecha', 'descripcion')
        }),
        ('Evidencias', {
            'fields': ('archivo', 'url_demo', 'visible')
        }),
    )

@admin.register(VentaGarage)
class VentaGarageAdmin(admin.ModelAdmin):
    # Aquí es muy útil ver el stock y precio rápido
    list_display = ('nombre_producto', 'precio', 'estado', 'stock', 'fecha_publicacion', 'activo')
    list_filter = ('estado', 'activo')
    search_fields = ('nombre_producto', 'item_id', 'descripcion')
    list_editable = ('precio', 'stock', 'activo') # Edita precios y stock sin entrar al producto
    list_per_page = 20
    readonly_fields = ()
    fieldsets = (
        ('Información del Producto', {
            'fields': ('nombre_producto', 'item_id', 'estado', 'descripcion')
        }),
        ('Inventario y Precio', {
            'fields': ('precio', 'stock')
        }),
        ('Multimedia y Visibilidad', {
            'fields': ('imagen', 'fecha_publicacion', 'activo')
        }),
    )


@admin.register(ProductoAcademico)
class ProductoAcademicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'clasificador', 'visible')
    list_filter = ('clasificador', 'visible')
    search_fields = ('nombre', 'clasificador', 'descripcion')
    list_editable = ('visible',)

    fieldsets = (
        ('Información del Recurso', {
            'fields': ('nombre', 'clasificador', 'descripcion')
        }),
        ('Visibilidad', {
            'fields': ('visible',)
        }),
    )