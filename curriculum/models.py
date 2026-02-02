from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import cloudinary.utils
from django.core.validators import FileExtensionValidator

# ============================================== #
# 1. DATOS PERSONALES (Con lógica de privacidad) #
# ============================================== #
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
    cedula = models.CharField(max_length=13, verbose_name="Cédula / ID", unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    sexo = models.CharField(max_length=20, choices=SEXO_CHOICES)
    estado_civil = models.CharField(max_length=30, choices=ESTADO_CIVIL_CHOICES)
    
    # Origen y Fecha
    nacionalidad = models.CharField(max_length=50, default="Ecuatoriano")
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
    
    # 2. MODIFICACIÓN: Agregamos este método para validar la fecha
    def clean(self):
        # Validar que la fecha de nacimiento no sea futura
        if self.fecha_nacimiento and self.fecha_nacimiento > timezone.now().date():
            raise ValidationError({'fecha_nacimiento': 'No puedes nacer en el futuro.'})


# ========================================= #
# 2. EXPERIENCIA (Con validación de fechas) #
# ========================================= #
class ExperienciaLaboral(models.Model):
    cargo = models.CharField(max_length=150, default="Cargo no especificado")
    empresa = models.CharField(max_length=150, default="Empresa no especificada")
    # ADAPTACIÓN: Cambiado a DateField para validación lógica
    fecha_inicio = models.DateField(default=timezone.now) 
    fecha_fin = models.DateField(null=True, blank=True, help_text="Dejar en blanco si es el trabajo actual")
    descripcion = models.TextField(default="Sin descripción de funciones")
    ubicacion = models.CharField(max_length=100, default="Ubicación no especificada")
    email_empresa = models.EmailField(max_length=100, null=True, blank=True, verbose_name="Email Empresa")
    sitio_web_empresa = models.URLField(max_length=100, null=True, blank=True, verbose_name="Sitio Web")
    nombre_contacto = models.CharField(max_length=100, null=True, blank=True, verbose_name="Nombre Contacto")
    telefono_contacto = models.CharField(max_length=60, null=True, blank=True, verbose_name="Teléfono Contacto")
    
    # Switch de visibilidad
    visible = models.BooleanField(default=True, verbose_name="Mostrar en CV")

    certificado = models.FileField(
        upload_to='experiencia/certificados/', 
        null=True, 
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        verbose_name="Certificado Laboral (PDF)"
    )

    class Meta:
        verbose_name_plural = "Experiencias Laborales"
        ordering = ['-fecha_inicio']

    def clean(self):
        # Obtenemos la fecha de hoy para comparar
        hoy = timezone.now().date()

        # 1. Restricción: Fecha Fin no puede ser menor a Fecha Inicio
        if self.fecha_fin and self.fecha_inicio and self.fecha_fin < self.fecha_inicio:
            raise ValidationError({
                'fecha_fin': 'Error: La fecha de finalización no puede ser antes de haber empezado.'
            })

        # 2. Restricción: Fecha Fin no puede ser futura (Nadie termina un trabajo mañana)
        if self.fecha_fin and self.fecha_fin > hoy:
            raise ValidationError({
                'fecha_fin': 'Error: La fecha de finalización no puede ser una fecha futura.'
            })

        # 3. (Opcional pero recomendada) Fecha Inicio tampoco debería ser futura
        if self.fecha_inicio and self.fecha_inicio > hoy:
             raise ValidationError({
                'fecha_inicio': 'Error: La fecha de inicio no puede estar en el futuro.'
            })

    def __str__(self):
        estado = " (Actual)" if not self.fecha_fin else ""
        return f"{self.cargo} en {self.empresa}{estado}"


# ================================== #
# 3. ESTUDIOS (Con lógica de fechas) #
# ================================== #
class EstudioRealizado(models.Model):
    titulo = models.CharField(max_length=200)
    institucion = models.CharField(max_length=200)
    descripcion = models.TextField(null=True, blank=True, verbose_name="Descripción / Logros")
    # ADAPTACIÓN: Cambiado a DateField
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True, help_text="Dejar vacío si sigues estudiando")
    archivo = models.FileField(
        upload_to='proyectos/archivos/', 
        null=True, 
        blank=True,
        # Aquí definimos las extensiones permitidas:
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text="Sube documentación o capturas (Formatos permitidos: PDF, JPG, JPEG, PNG)",
        verbose_name="Archivo o Evidencia"
    )
    
    visible = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Estudios Realizados"
        ordering = ['-fecha_fin']

    def clean(self):
        hoy = timezone.now().date()
        
        # 1. Validación: Fecha Fin no futura
        if self.fecha_fin and self.fecha_fin > hoy:
            raise ValidationError({'fecha_fin': 'La fecha de graduación no puede ser futura.'})

        # 2. Validación: Coherencia de fechas
        if self.fecha_fin and self.fecha_inicio and self.fecha_fin < self.fecha_inicio:
            raise ValidationError({'fecha_fin': 'La fecha de graduación no puede ser anterior al inicio.'})

    def __str__(self):
        return self.titulo


# ====================================== #
# 4. CURSOS (Simplificado pero ordenado) #
# ====================================== #

class CursoCapacitacion(models.Model):
    nombre_curso = models.CharField(max_length=200)
    institucion = models.CharField(max_length=200)
    horas = models.PositiveIntegerField(help_text="Cantidad de horas académicas") # Cambiado a número para poder sumar totales si quisieras
    fecha_inicio = models.DateField(default=timezone.now, verbose_name="Fecha Inicio")
    fecha_fin = models.DateField(default=timezone.now, verbose_name="Fecha Fin")
    descripcion = models.TextField(null=True, blank=True, verbose_name="Descripción del Curso")
    nombre_contacto = models.CharField(max_length=100, null=True, blank=True, verbose_name="Nombre Contacto (Auspicia)")
    telefono_contacto = models.CharField(max_length=60, null=True, blank=True, verbose_name="Teléfono Contacto")
    email_empresa = models.CharField(max_length=60, null=True, blank=True, verbose_name="Email Empresa Patrocinadora")
    # --- CERTIFICADO (Restricción: Solo PDF) ---
    certificado_pdf = models.FileField(
        upload_to='cursos/certificados/', 
        null=True, 
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="Sube el certificado del curso en formato PDF"
    )
    visible = models.BooleanField(default=True)
    class Meta:
        verbose_name_plural = "Cursos y Formaciones"
        ordering = ['-fecha_fin'] # Ordenamos por fecha de finalización

    def clean(self):
        hoy = timezone.now().date()

        # 1. RESTRICCIÓN: Fecha Fin no puede ser futura
        if self.fecha_fin and self.fecha_fin > hoy:
            raise ValidationError({'fecha_fin': 'La fecha de finalización no puede ser una fecha futura.'})

        # 2. RESTRICCIÓN: Coherencia temporal (Inicio vs Fin)
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_inicio > self.fecha_fin:
                raise ValidationError({
                    'fecha_inicio': 'La fecha de inicio no puede ser mayor a la fecha de fin.',
                    'fecha_fin': 'La fecha de fin no puede ser menor a la de inicio.'
                })

    def __str__(self):
        return self.nombre_curso

    # --- Vista Previa (Sin cambios, para que siga funcionando tu admin) ---
    @property
    def get_preview_url(self):
        if self.certificado_pdf and hasattr(self.certificado_pdf, 'name'):
            try:
                url, options = cloudinary.utils.cloudinary_url(
                    self.certificado_pdf.name,
                    resource_type="image", 
                    format="jpg"           
                )
                return url
            except Exception:
                return self.certificado_pdf.url
        return None


# ================== #
# 5. RECONOCIMIENTOS #
# ================== #
class Reconocimiento(models.Model):
    nombre = models.CharField(max_length=200, default="Reconocimiento no especificado")
    institucion = models.CharField(max_length=200, default="Institución no especificada")
    fecha = models.DateField(default=timezone.now) 
    codigo_registro = models.CharField(max_length=50, blank=True, default="")
    descripcion = models.TextField(null=True, blank=True, verbose_name="Descripción del Reconocimiento")
    nombre_contacto = models.CharField(max_length=100, null=True, blank=True, verbose_name="Nombre Contacto Auspicia")
    telefono_contacto = models.CharField(max_length=60, null=True, blank=True, verbose_name="Teléfono Contacto Auspicia")
    
    certificado_pdf = models.FileField(
        upload_to='reconocimientos/certificados/', 
        null=True, 
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="Sube el diploma o certificado en formato PDF"
    )
    
    visible = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Reconocimientos y Premios"
        ordering = ['-fecha']

    def clean(self):
        # 3. RESTRICCIÓN: Fecha no futura
        if self.fecha and self.fecha > timezone.now().date():
            raise ValidationError({'fecha': 'La fecha del reconocimiento no puede ser una fecha futura.'})

    def __str__(self):
        return self.nombre
    
    # Propiedad para vista previa (se mantiene igual para que funcione tu admin)
    @property
    def get_preview_url(self):
        if self.certificado_pdf and hasattr(self.certificado_pdf, 'name'):
            try:
                url, options = cloudinary.utils.cloudinary_url(
                    self.certificado_pdf.name,
                    resource_type="image", 
                    format="jpg"           
                )
                return url
            except Exception:
                return self.certificado_pdf.url
        return None


# ======================== #
# 6. PRODUCTOS / PROYECTOS #
# ======================== #
class ProductoLaboral(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha = models.DateField(default=timezone.now)
    
    # 2. RESTRICCIÓN DE ARCHIVOS (PDF + Imágenes)
    archivo = models.FileField(
        upload_to='proyectos/archivos/', 
        null=True, 
        blank=True,
        # Aquí definimos las extensiones permitidas:
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text="Sube documentación o capturas (Formatos permitidos: PDF, JPG, JPEG, PNG)",
        verbose_name="Archivo o Evidencia"
    )
    
    url_demo = models.URLField(null=True, blank=True, help_text="Link al proyecto en vivo si existe")
    visible = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Productos Laborales"
        ordering = ['-fecha']

    def clean(self):
        # 3. RESTRICCIÓN DE FECHA FUTURA
        if self.fecha and self.fecha > timezone.now().date():
            raise ValidationError({'fecha': 'La fecha del proyecto no puede ser futura.'})

    def __str__(self):
        return self.nombre


# ============================================= #
# 7. VENTA DE GARAGE (Con validación de precio) #
# ============================================= #
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
    fecha_publicacion = models.DateTimeField(
        default=timezone.now, 
        verbose_name="Fecha de Publicación"
    )
    activo = models.BooleanField(default=True, help_text="Desactívalo para ocultarlo de la tienda sin borrarlo")

    class Meta:
        verbose_name_plural = "Venta de Garage"
        ordering = ['-fecha_publicacion'] # Ordenamos del más reciente al más antiguo

    def clean(self):
        # 1. Validación de Precio
        if self.precio is not None and self.precio < 0:
            raise ValidationError({'precio': 'El precio no puede ser negativo.'})

        # 2. Validación de Fecha Futura (NUEVA)
        if self.fecha_publicacion and self.fecha_publicacion > timezone.now():
            raise ValidationError({'fecha_publicacion': 'La fecha de publicación no puede ser futura.'})

    def __str__(self):
        return f"{self.nombre_producto} (${self.precio})"
    


# ======================= #
# 8. PRODUCTOS ACADÉMICOS #
# ======================= #
class ProductoAcademico(models.Model):
    # Basado en 'nombrerecurso'
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Recurso")
    
    # Basado en 'clasificador'
    clasificador = models.CharField(max_length=100, verbose_name="Clasificador / Categoría")
    
    # Basado en 'descripcion' (Le puse TextField por si necesitas escribir más de 100 letras)
    descripcion = models.TextField(verbose_name="Descripción", max_length=500)
    
    # Basado en 'activarparaqueseveaenfront'
    visible = models.BooleanField(default=True, verbose_name="Mostrar en CV")

    class Meta:
        verbose_name_plural = "Productos Académicos"

    def __str__(self):
        return self.nombre