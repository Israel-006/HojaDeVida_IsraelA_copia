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
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

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
    reconocimientos = Reconocimiento.objects.filter(visible=True).order_by('-fecha')
    return render(request, 'curriculum/reconocimientos.html', {'perfil': perfil, 'reconocimientos': reconocimientos})

def trabajos(request):
    perfil = DatosPersonales.objects.first()
    # ORDEN: Usamos el definido en models.py (-fecha)
    proyectos = ProductoLaboral.objects.all()
    return render(request, 'curriculum/proyectos.html', {'perfil': perfil, 'trabajos': proyectos})

def venta(request):
    perfil = DatosPersonales.objects.first()
    # Ventas sí ordenamos por ID (último agregado)
    productos = VentaGarage.objects.all().order_by('-fecha_publicacion')
    return render(request, 'curriculum/venta.html', {'perfil': perfil, 'servicios': productos})

def contacto(request):
    perfil = DatosPersonales.objects.first()
    return render(request, 'curriculum/contacto.html', {'perfil': perfil})

def numerar_paginas(pdf_writer):
    """
    Recibe un PdfWriter con todo el contenido mezclado,
    cuenta las páginas reales y estampa "Página X de Y" al final.
    """
    # 1. Guardamos el contenido actual en memoria para leerlo
    temp_buffer = BytesIO()
    pdf_writer.write(temp_buffer)
    temp_buffer.seek(0)
    reader = PdfReader(temp_buffer)
    total_pages = len(reader.pages)
    
    # 2. Creamos un nuevo escritor final
    final_writer = PdfWriter()

    # 3. Iteramos cada página existente
    for i, page in enumerate(reader.pages):
        # Crear un "lienzo" (canvas) temporal solo para el número
        packet = BytesIO()
        # Usamos A4. Si tus PDFs adjuntos son de otro tamaño, esto se pondrá al fondo centrado en A4
        can = canvas.Canvas(packet, pagesize=A4)
        
        # Configuración del texto (Gris, pequeño, centrado)
        can.setFillColorRGB(0.5, 0.5, 0.5) 
        can.setFont("Helvetica", 9)
        
        # Texto: Página X de Total
        texto = f"Página {i+1} de {total_pages}"
        
        # Dibujar centrado en la parte inferior (A4[0] es el ancho)
        # 15mm desde abajo
        can.drawCentredString(A4[0] / 2, 15 * mm, texto)
        can.save()

        # Mover al inicio del buffer del número
        packet.seek(0)
        number_pdf = PdfReader(packet)
        page_number_layer = number_pdf.pages[0]

        # 4. FUSIONAR: Pegamos el número encima de la página original
        page.merge_page(page_number_layer)
        final_writer.add_page(page)

    return final_writer

# ==========================================
# GENERADOR DE PDF (CORREGIDO PARA RENDER Y CLOUDINARY)
# ==========================================
def generar_cv(request):
    perfil = DatosPersonales.objects.first()
    
    # 1. FILTROS Y OBTENCIÓN DE DATOS (Asegurando que traemos la fecha de venta)
    incluir_exp = request.GET.get('experiencia') == 'on' if request.GET.get('origen') == 'personalizado' else True
    incluir_edu = request.GET.get('educacion') == 'on' if request.GET.get('origen') == 'personalizado' else True
    incluir_rec = request.GET.get('reconocimientos') == 'on' if request.GET.get('origen') == 'personalizado' else True
    incluir_pro = request.GET.get('proyectos') == 'on' if request.GET.get('origen') == 'personalizado' else True
    incluir_ven = request.GET.get('venta') == 'on' if request.GET.get('origen') == 'personalizado' else True

    experiencias = ExperienciaLaboral.objects.filter(visible=True) if incluir_exp else []
    estudios = EstudioRealizado.objects.filter(visible=True) if incluir_edu else []
    cursos_lista = CursoCapacitacion.objects.filter(visible=True).order_by('-fecha_realizacion') if incluir_edu else []
    reconocimientos = Reconocimiento.objects.filter(visible=True) if incluir_rec else []
    proyectos = ProductoLaboral.objects.filter(visible=True) if incluir_pro else []
    
    # Ventas ordenadas por fecha de publicación (Punto 3)
    ventas = VentaGarage.objects.filter(activo=True).order_by('-fecha_publicacion') if incluir_ven else []

    pdf_writer = PdfWriter()
    template = get_template('curriculum/cv_pdf.html') 

    # --- PASO 1: PARTE SUPERIOR (DATOS, EXP, EDUCACIÓN) ---
    context_part1 = {
        'perfil': perfil,
        'experiencias': experiencias,
        'estudios': estudios,
        'section_mode': 'top',
        'MEDIA_URL': settings.MEDIA_URL,
    }
    html_1 = template.render(context_part1)
    buffer_1 = BytesIO()
    pisa.CreatePDF(html_1, dest=buffer_1, link_callback=link_callback)
    buffer_1.seek(0)
    for page in PdfReader(buffer_1).pages:
        pdf_writer.add_page(page)

    # --- PASO 2: CURSOS EN CADENA (Punto 1 y 2 del rediseño) ---
    # Esto quita el mensaje de "adjunto" y los pone seguidos con descripción y fechas
    if cursos_lista:
        context_cursos = {
            'perfil': perfil,
            'cursos': cursos_lista,
            'section_mode': 'courses_list', 
            'MEDIA_URL': settings.MEDIA_URL,
        }
        html_c = template.render(context_cursos)
        buffer_c = BytesIO()
        pisa.CreatePDF(html_c, dest=buffer_c, link_callback=link_callback)
        buffer_c.seek(0)
        for page in PdfReader(buffer_c).pages:
            pdf_writer.add_page(page)

    # --- PASO 3: PARTE INFERIOR (RECONOCIMIENTOS, PROYECTOS, VENTAS CON FECHA) ---
    if reconocimientos or proyectos or ventas:
        context_part3 = {
            'perfil': perfil,
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
        for page in PdfReader(buffer_3).pages:
            pdf_writer.add_page(page)

    # --- PASO 4: ÍNDICE DE CERTIFICADOS (Nuevo requerimiento) ---
    # Crea la lista numerada cronológica de "Certificados" para no dejar la hoja en blanco
    if cursos_lista and any(c.certificado_pdf for c in cursos_lista):
        context_idx = {
            'perfil': perfil,
            'cursos': cursos_lista,
            'section_mode': 'certificates_index',
        }
        html_idx = template.render(context_idx)
        buffer_idx = BytesIO()
        pisa.CreatePDF(html_idx, dest=buffer_idx, link_callback=link_callback)
        buffer_idx.seek(0)
        reader_idx = PdfReader(buffer_idx)
        # Solo añadimos si el PDF generado tiene contenido real
        if len(reader_idx.pages) > 0:
            for page in reader_idx.pages:
                pdf_writer.add_page(page)

    # --- PASO 5: ADJUNTAR LOS PDFs ORIGINALES DESDE CLOUDINARY ---
    for curso in cursos_lista:
        if curso.certificado_pdf:
            try:
                pdf_url = curso.certificado_pdf.url
                response_pdf = requests.get(pdf_url, timeout=10)
                if response_pdf.status_code == 200:
                    cert_buffer = BytesIO(response_pdf.content)
                    reader_cert = PdfReader(cert_buffer)
                    for page in reader_cert.pages:
                        pdf_writer.add_page(page)
            except Exception as e:
                print(f"Error adjuntando certificado de {curso.nombre_curso}: {e}")

    # --- PASO 6: FINALIZAR Y ENVIAR ---
    try:
        pdf_writer_numerado = numerar_paginas(pdf_writer)
    except Exception as e:
        print(f"Error numerando páginas: {e}")
        pdf_writer_numerado = pdf_writer 

    final_buffer = BytesIO()
    pdf_writer_numerado.write(final_buffer)
    
    response = HttpResponse(final_buffer.getvalue(), content_type='application/pdf')
    safe_name = "".join([c for c in perfil.nombres if c.isalnum() or c in (' ', '_')]).strip()
    filename = f"CV_Personalizado_{safe_name}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response