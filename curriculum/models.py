from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import cloudinary.utils
from django.core.validators import FileExtensionValidator

# ==========================================
# 1. DATOS PERSONALES (Con lógica de privacidad)
# ==========================================
class DatosPersonales(models.Model):
    SEXO_CHOICES = [
        ('Mujer', 'Mujer'),
        ('Hombre', 'Hombre'),
        ('Otro', 'Otro'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        ('Soltero/a', 'Soltero/a'),  # <--- CAMBIA ESTA LÍNEA
        ('Casado/a', 'Casado/a'),    # También puedes aprovechar para corregir estos si quieres
        ('Divorciado/a', 'Divorciado/a'),
        ('Viudo/a', 'Viudo/a'),
        ('Unión Libre', 'Unión Libre'),
    ]

    # Identidad Básica
    cedula = models.CharField(max_length=13, verbose_name="Cédula / ID")
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    sexo = models.CharField(max_length=20, choices=SEXO_CHOICES)
    estado_civil = models.CharField(max_length=30, choices=ESTADO_CIVIL_CHOICES)
    
    # Origen y Fecha
    nacionalidad = models.CharField(max_length=50, default="Ecuatoriana")
    lugar_nacimiento = models.CharField(max_length=100, default="No especificado")
    fecha_nacimiento = models.DateField(null=True, blank=True)
    
    # Contacto
    telefono = models.CharField(max_length=15, verbose_name="Teléfono Celular")
    telefono_convencional = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(verbose_name="Correo Electrónico")
    sitio_web = models.URLField(null=True, blank=True)
    
    # Ubicación
    direccion = models.TextField(verbose_name="Dirección Domiciliaria")
    direccion_trabajo = models.TextField(null=True, blank=True, verbose_name="Dirección Laboral")
    licencia = models.CharField(max_length=50, null=True, blank=True, verbose_name="Licencia de Conducir")
    
    # Multimedia y Perfil
    foto = models.ImageField(upload_to='perfil/', null=True, blank=True)
    descripcion_perfil = models.TextField(null=True, blank=True, verbose_name="Perfil Profesional (Bio)")
    
    # Redes Sociales
    url_linkedin = models.URLField(null=True, blank=True, verbose_name="URL LinkedIn")
    url_instagram = models.URLField(null=True, blank=True, verbose_name="URL Instagram")
    url_github = models.URLField(null=True, blank=True, verbose_name="URL GitHub")

    # === LÓGICA IMPORTADA: Switches de Privacidad ===
    mostrar_direccion_domiciliaria = models.BooleanField(default=False, help_text="Si está activo, se mostrará la dirección de casa en la web.")
    mostrar_telefono = models.BooleanField(default=True, help_text="Mostrar teléfono celular en la web.")

    class Meta:
        verbose_name = "Datos Personales"
        verbose_name_plural = "Datos Personales"

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


# ==========================================
# 2. EXPERIENCIA (Con validación de fechas)
# ==========================================
class ExperienciaLaboral(models.Model):
    cargo = models.CharField(max_length=150, default="Cargo no especificado")
    empresa = models.CharField(max_length=150, default="Empresa no especificada")
    # ADAPTACIÓN: Cambiado a DateField para validación lógica
    fecha_inicio = models.DateField(default=timezone.now) 
    fecha_fin = models.DateField(null=True, blank=True, help_text="Dejar en blanco si es el trabajo actual")
    descripcion = models.TextField(default="Sin descripción de funciones")
    ubicacion = models.CharField(max_length=100, default="Ubicación no especificada")
    
    # Switch de visibilidad
    visible = models.BooleanField(default=True, verbose_name="Mostrar en CV")

    class Meta:
        verbose_name_plural = "Experiencias Laborales"
        ordering = ['-fecha_inicio'] # Ordenar del más reciente al más antiguo

    def clean(self):
        # LÓGICA IMPORTADA: Validar que no haya fechas imposibles
        if self.fecha_fin and self.fecha_inicio and self.fecha_fin < self.fecha_inicio:
            raise ValidationError({'fecha_fin': 'La fecha de fin no puede ser anterior a la de inicio.'})

    def __str__(self):
        estado = " (Actual)" if not self.fecha_fin else ""
        return f"{self.cargo} en {self.empresa}{estado}"


# ==========================================
# 3. ESTUDIOS (Con lógica de fechas)
# ==========================================
class EstudioRealizado(models.Model):
    titulo = models.CharField(max_length=200)
    institucion = models.CharField(max_length=200)
    # ADAPTACIÓN: Cambiado a DateField
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True, help_text="Dejar vacío si sigues estudiando")
    certificado_pdf = models.FileField(
        upload_to='educacion/certificados/', 
        null=True, 
        blank=True,
        help_text="Sube aquí el diploma o certificado en formato PDF"
    )
    visible = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Estudios Realizados"
        ordering = ['-fecha_fin']

    def clean(self):
        if self.fecha_fin and self.fecha_inicio and self.fecha_fin < self.fecha_inicio:
            raise ValidationError("La fecha de graduación no puede ser anterior al inicio.")

    def __str__(self):
        return self.titulo


# ==========================================
# 4. CURSOS (Simplificado pero ordenado)
# ==========================================

class CursoCapacitacion(models.Model):
    nombre_curso = models.CharField(max_length=200)
    institucion = models.CharField(max_length=200)
    horas = models.PositiveIntegerField(help_text="Cantidad de horas académicas") # Cambiado a número para poder sumar totales si quisieras
    fecha_realizacion = models.DateField(default=timezone.now) # Agregado para ordenar
    certificado_pdf = models.FileField(
        upload_to='cursos/certificados/', 
        null=True, 
        blank=True,
        help_text="Sube el certificado del curso en formato PDF"
    )
    visible = models.BooleanField(default=True)
    class Meta:
        verbose_name_plural = "Cursos y Formaciones"
        ordering = ['-fecha_realizacion']

    def __str__(self):
        return self.nombre_curso
    @property
    def get_preview_url(self):
        if self.certificado_pdf and hasattr(self.certificado_pdf, 'name'):
            try:
                # Cloudinary necesita el 'public_id' (el nombre del archivo en la nube)
                # Al usar FileField, 'self.certificado_pdf.name' suele tener ese valor.
                
                # Generamos una URL limpia solicitando formato JPG
                url, options = cloudinary.utils.cloudinary_url(
                    self.certificado_pdf.name,
                    resource_type="image", # Forzamos a que lo trate como imagen
                    format="jpg"           # Lo convertimos a JPG
                )
                return url
            except Exception as e:
                print(f"Error generando preview: {e}")
                # Si falla, intentamos devolver la URL original como fallback
                return self.certificado_pdf.url
        return None


# ==========================================
# 5. RECONOCIMIENTOS
# ==========================================
class Reconocimiento(models.Model):
    nombre = models.CharField(max_length=200, default="Reconocimiento no especificado")
    institucion = models.CharField(max_length=200, default="Institución no especificada")
    fecha = models.DateField(default=timezone.now) # Adaptado a fecha real
    codigo_registro = models.CharField(max_length=50, blank=True, default="")
    visible = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Reconocimientos y Premios"
        ordering = ['-fecha']

    def __str__(self):
        return self.nombre


# ==========================================
# 6. PRODUCTOS / PROYECTOS
# ==========================================
class ProductoLaboral(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha = models.DateField(default=timezone.now)
    registro_id = models.CharField(max_length=50, blank=True, null=True)
    
    # --- AQUÍ ESTÁ EL CAMBIO ---
    archivo = models.FileField(
        upload_to='proyectos/archivos/', 
        null=True, 
        blank=True,
        # Agregamos el validador para restringir a solo PDF:
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="Documentación del proyecto (Solo archivos PDF)"
    )
    
    url_demo = models.URLField(null=True, blank=True, help_text="Link al proyecto en vivo si existe")
    visible = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Productos Laborales"
        ordering = ['-fecha']

    def __str__(self):
        return self.nombre


# ==========================================
# 7. VENTA DE GARAGE (Con validación de precio)
# ==========================================
class VentaGarage(models.Model):
    ESTADO_CHOICES = [
        ('Nuevo', 'Nuevo'), 
        ('Bueno', 'Bueno'), 
        ('Regular', 'Regular')
    ]
    
    nombre_producto = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES)
    item_id = models.CharField(max_length=50, unique=True) # Agregado unique para evitar duplicados
    imagen = models.ImageField(upload_to='venta/', null=True, blank=True)
    stock = models.PositiveIntegerField(default=1, help_text="Cantidad disponible")
    fecha_publicacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Publicación")
    activo = models.BooleanField(default=True, help_text="Desactívalo para ocultarlo de la tienda sin borrarlo")

    class Meta:
        verbose_name_plural = "Venta de Garage"

    def clean(self):
        if self.precio < 0:
            raise ValidationError("El precio no puede ser negativo.")

    def __str__(self):
        return f"{self.nombre_producto} (${self.precio})"