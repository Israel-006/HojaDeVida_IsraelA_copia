import os
import requests  # <--- IMPORTANTE: Necesario para descargar los archivos de Cloudinary
from io import BytesIO
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders # Para buscar estáticos de forma segura
from .models import (
    DatosPersonales, ExperienciaLaboral, EstudioRealizado, 
    CursoCapacitacion, Reconocimiento, ProductoLaboral, VentaGarage
)
from pypdf import PdfWriter, PdfReader

# ==========================================
# FUNCIÓN PARA GESTIONAR RUTAS (IMÁGENES Y CSS)
# ==========================================
def link_callback(uri, rel):
    """
    Ayuda a xhtml2pdf a encontrar las imágenes y estilos.
    Soporta archivos locales (Static) y remotos (Cloudinary).
    """
    # 1. Si es una URL completa (ej: Cloudinary https://res.cloudinary...), déjala pasar
    if uri.startswith('http'):
        return uri

    # 2. Configuración de rutas locales
    sUrl = settings.STATIC_URL        # /static/
    sRoot = settings.STATIC_ROOT      # carpeta staticfiles/
    mUrl = settings.MEDIA_URL         # /media/
    mRoot = settings.MEDIA_ROOT       # carpeta media/

    # 3. Intentar convertir URL relativa a ruta absoluta del sistema
    path = None
    
    # Caso A: Es un archivo Media (pero local)
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    
    # Caso B: Es un archivo Estático (CSS, JS, Logos del sitio)
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))

    # 4. Verificar si el archivo existe en esa ruta construida
    if path and os.path.isfile(path):
        return path

    # 5. SALVAVIDAS: Si no lo encontró en STATIC_ROOT, búscalo con los finders de Django
    # (Esto ayuda si collectstatic falló o la ruta es distinta)
    if uri.startswith(sUrl):
        found_path = finders.find(uri.replace(sUrl, ""))
        if found_path:
            return found_path

    # Si todo falla, devuelve la URI original (xhtml2pdf intentará resolverla)
    return uri

# ==========================================
# VISTAS DE LA PÁGINA WEB
# ==========================================

def inicio(request):
    perfil = DatosPersonales.objects.first()
    return render(request, 'curriculum/inicio.html', {'perfil': perfil})

def perfil(request):
    perfil = DatosPersonales.objects.first()
    return render(request, 'curriculum/datos_personales.html', {'perfil': perfil})

def experiencia(request):
    perfil = DatosPersonales.objects.first()
    # ORDEN: Usamos el definido en models.py (-fecha_inicio)
    experiencias = ExperienciaLaboral.objects.all()
    return render(request, 'curriculum/experiencia.html', {'perfil': perfil, 'experiencias': experiencias})

def educacion(request):
    perfil = DatosPersonales.objects.first()
    # ORDEN: Usamos el definido en models.py (-fecha_fin)
    estudios = EstudioRealizado.objects.all()
    return render(request, 'curriculum/educacion.html', {'perfil': perfil, 'educacion': estudios})

def cursos(request):
    perfil = DatosPersonales.objects.first()
    # ORDEN: Usamos el definido en models.py (-fecha_realizacion)
    cursos = CursoCapacitacion.objects.all()
    return render(request, 'curriculum/cursos.html', {'perfil': perfil, 'cursos': cursos})

def reconocimientos(request):
    perfil = DatosPersonales.objects.first()
    # ORDEN: Usamos el definido en models.py (-fecha)
    reconocimientos = Reconocimiento.objects.all()
    return render(request, 'curriculum/reconocimientos.html', {'perfil': perfil, 'reconocimientos': reconocimientos})

def trabajos(request):
    perfil = DatosPersonales.objects.first()
    # ORDEN: Usamos el definido en models.py (-fecha)
    proyectos = ProductoLaboral.objects.all()
    return render(request, 'curriculum/proyectos.html', {'perfil': perfil, 'trabajos': proyectos})

def venta(request):
    perfil = DatosPersonales.objects.first()
    # Ventas sí ordenamos por ID (último agregado)
    productos = VentaGarage.objects.all().order_by('-id')
    return render(request, 'curriculum/venta.html', {'perfil': perfil, 'servicios': productos})

def contacto(request):
    perfil = DatosPersonales.objects.first()
    return render(request, 'curriculum/contacto.html', {'perfil': perfil})


# ==========================================
# GENERADOR DE PDF (CORREGIDO PARA RENDER Y CLOUDINARY)
# ==========================================
def generar_cv(request):
    perfil = DatosPersonales.objects.first()
    
    # 1. VERIFICAR EL ORIGEN Y FILTROS
    if request.GET.get('origen') == 'personalizado':
        incluir_exp = request.GET.get('experiencia') == 'on'
        incluir_edu = request.GET.get('educacion') == 'on'
        incluir_rec = request.GET.get('reconocimientos') == 'on'
        incluir_pro = request.GET.get('proyectos') == 'on'
        incluir_ven = request.GET.get('venta') == 'on'
    else:
        # Por defecto incluir todo
        incluir_exp = True
        incluir_edu = True
        incluir_rec = True
        incluir_pro = True
        incluir_ven = True

    # 2. OBTENER DATOS DE LA BD (Respetando el orden cronológico de los Modelos)
    experiencias = ExperienciaLaboral.objects.all() if incluir_exp else []
    estudios = EstudioRealizado.objects.all() if incluir_edu else []
    cursos_lista = CursoCapacitacion.objects.all() if incluir_edu else []
    reconocimientos = Reconocimiento.objects.all() if incluir_rec else []
    proyectos = ProductoLaboral.objects.all() if incluir_pro else []
    ventas = VentaGarage.objects.all().order_by('-id') if incluir_ven else []

    # Preparamos el escritor de PDF final
    pdf_writer = PdfWriter()
    template = get_template('curriculum/cv_pdf.html') 

    # --- PASO 1: GENERAR LA PARTE SUPERIOR (PERFIL, EXP, EDUCACIÓN) ---
    context_part1 = {
        'perfil': perfil,
        'experiencias': experiencias,
        'estudios': estudios,
        'cursos': [], # Los cursos van aparte intercalados
        'reconocimientos': [],
        'proyectos': [],
        'ventas': [],
        'section_mode': 'top',
        'MEDIA_URL': settings.MEDIA_URL,
    }
    
    html_1 = template.render(context_part1)
    buffer_1 = BytesIO()
    # Generamos el PDF en memoria
    pisa_status = pisa.CreatePDF(html_1, dest=buffer_1, link_callback=link_callback)
    
    if pisa_status.err:
        return HttpResponse('Error generando la primera parte del PDF', status=500)

    buffer_1.seek(0)
    reader_1 = PdfReader(buffer_1)
    for page in reader_1.pages:
        pdf_writer.add_page(page)

    # --- PASO 2: INSERTAR CURSOS Y ADJUNTAR CERTIFICADOS ---
    if cursos_lista:
        for curso in cursos_lista:
            # A. Generar la página con la info del curso (Título, horas, institución)
            context_curso = {
                'perfil': perfil,
                'cursos': [curso],
                'section_mode': 'course_single',
                'MEDIA_URL': settings.MEDIA_URL,
            }
            html_curso = template.render(context_curso)
            buffer_curso = BytesIO()
            pisa.CreatePDF(html_curso, dest=buffer_curso, link_callback=link_callback)
            buffer_curso.seek(0)
            
            reader_curso = PdfReader(buffer_curso)
            for page in reader_curso.pages:
                pdf_writer.add_page(page)

            # B. Adjuntar el PDF del certificado (DESDE LA NUBE - CLOUDINARY)
            if curso.certificado_pdf:
                try:
                    # Usamos la URL pública de Cloudinary
                    pdf_url = curso.certificado_pdf.url
                    
                    # Descargamos el archivo en el momento
                    response = requests.get(pdf_url)
                    
                    if response.status_code == 200:
                        # Convertimos el contenido descargado en un archivo en memoria
                        cert_buffer = BytesIO(response.content)
                        reader_cert = PdfReader(cert_buffer)
                        
                        # Agregamos cada página del certificado al PDF final
                        for page in reader_cert.pages:
                            pdf_writer.add_page(page)
                    else:
                        print(f"No se pudo descargar el certificado: {pdf_url}")

                except Exception as e:
                    # Si falla un certificado, el CV se genera igual, solo se salta ese archivo
                    print(f"Error adjuntando certificado del curso {curso.nombre_curso}: {e}")

    # --- PASO 3: PARTE INFERIOR (RECONOCIMIENTOS, PROYECTOS, ETC) ---
    if reconocimientos or proyectos or ventas:
        context_part3 = {
            'perfil': perfil,
            'experiencias': [],
            'estudios': [],
            'cursos': [],
            'reconocimientos': reconocimientos,
            'proyectos': proyectos,
            'ventas': ventas,
            'section_mode': 'bottom',
            'MEDIA_URL': settings.MEDIA_URL,
        }
        
        html_3 = template.render(context_part3)
        buffer_3 = BytesIO()
        pisa.CreatePDF(html_3, dest=buffer_3, link_callback=link_callback)
        buffer_3.seek(0)
        reader_3 = PdfReader(buffer_3)
        for page in reader_3.pages:
            pdf_writer.add_page(page)

    # --- FINALIZAR Y ENVIAR ---
    final_buffer = BytesIO()
    pdf_writer.write(final_buffer)
    
    response = HttpResponse(final_buffer.getvalue(), content_type='application/pdf')
    # Limpiamos el nombre del archivo para evitar caracteres raros
    safe_name = "".join([c for c in perfil.nombres if c.isalnum() or c in (' ', '_')]).strip()
    filename = f"CV_Personalizado_{safe_name}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response