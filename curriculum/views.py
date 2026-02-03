import os
import requests
from io import BytesIO
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
from .models import (
    DatosPersonales, ExperienciaLaboral, EstudioRealizado, 
    CursoCapacitacion, Reconocimiento, ProductoLaboral, VentaGarage, ProductoAcademico
)
from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

# AHORA SÍ FUNCIONARÁ ESTA IMPORTACIÓN
from .cv_settings import get_cv_styles

# ==========================================
# UTILIDADES
# ==========================================
def link_callback(uri, rel):
    if uri.startswith('http'):
        return uri
    sUrl, sRoot = settings.STATIC_URL, settings.STATIC_ROOT
    mUrl, mRoot = settings.MEDIA_URL, settings.MEDIA_ROOT
    
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        path = ""

    if path and os.path.isfile(path):
        return path
    if uri.startswith(sUrl):
        found = finders.find(uri.replace(sUrl, ""))
        if found: return found
    return uri

def numerar_paginas(pdf_writer):
    temp_buffer = BytesIO()
    pdf_writer.write(temp_buffer)
    temp_buffer.seek(0)
    reader = PdfReader(temp_buffer)
    total_pages = len(reader.pages)
    final_writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        can.setFillColorRGB(0.5, 0.5, 0.5) 
        can.setFont("Helvetica", 9)
        can.drawCentredString(A4[0]/2, 15*mm, f"Página {i+1} de {total_pages}")
        can.save()
        packet.seek(0)
        page.merge_page(PdfReader(packet).pages[0])
        final_writer.add_page(page)
    return final_writer

# ==========================================
# VISTAS HTML
# ==========================================
def inicio(request):
    return render(request, 'curriculum/inicio.html', {'perfil': DatosPersonales.objects.first()})
def perfil(request):
    return render(request, 'curriculum/datos_personales.html', {'perfil': DatosPersonales.objects.first()})
def experiencia(request):
    return render(request, 'curriculum/experiencia.html', {'perfil': DatosPersonales.objects.first(), 'experiencias': ExperienciaLaboral.objects.all()})
def educacion(request):
    return render(request, 'curriculum/educacion.html', {'perfil': DatosPersonales.objects.first(), 'educacion': EstudioRealizado.objects.all()})
def cursos(request):
    return render(request, 'curriculum/cursos.html', {'perfil': DatosPersonales.objects.first(), 'cursos': CursoCapacitacion.objects.all()})
def reconocimientos(request):
    return render(request, 'curriculum/reconocimientos.html', {'perfil': DatosPersonales.objects.first(), 'reconocimientos': Reconocimiento.objects.filter(visible=True).order_by('-fecha')})
def trabajos(request):
    return render(request, 'curriculum/proyectos.html', {'perfil': DatosPersonales.objects.first(), 'trabajos': ProductoLaboral.objects.all()})
def venta(request):
    return render(request, 'curriculum/venta.html', {'perfil': DatosPersonales.objects.first(), 'servicios': VentaGarage.objects.all().order_by('-fecha_publicacion')})
def contacto(request):
    return render(request, 'curriculum/contacto.html', {'perfil': DatosPersonales.objects.first()})
def productos_academicos(request):
    return render(request, 'curriculum/productos_academicos.html', {
        'perfil': DatosPersonales.objects.first(),
        'productos_academicos': ProductoAcademico.objects.filter(visible=True)
    })

# ==========================================
# GENERADOR PDF
# ==========================================
def generar_cv(request):
    perfil = DatosPersonales.objects.first()
    styles = get_cv_styles(request)

    # 1. CAPTURAR FILTROS (Aquí estaba el fallo, faltaban varios)
    origen = request.GET.get('origen')
    is_custom = (origen == 'personalizado') # Variable auxiliar para limpieza

    # Si es personalizado, leemos el checkbox. Si no, asumimos True (mostrar todo).
    incluir_exp = request.GET.get('experiencia') == 'on' if is_custom else True
    incluir_edu = request.GET.get('educacion') == 'on' if is_custom else True
    
    # --- NUEVOS FILTROS CORREGIDOS ---
    incluir_rec = request.GET.get('reconocimientos') == 'on' if is_custom else True
    incluir_pro = request.GET.get('proyectos') == 'on' if is_custom else True
    incluir_ven = request.GET.get('venta') == 'on' if is_custom else True
    incluir_aca = request.GET.get('productos_academicos') == 'on' if is_custom else True
    
    # 2. CONSULTAS A BASE DE DATOS (Condicionadas)
    # Si la variable 'incluir_X' es False, pasamos una lista vacía []
    
    experiencias = ExperienciaLaboral.objects.filter(visible=True).order_by('-fecha_inicio') if incluir_exp else []
    
    estudios = EstudioRealizado.objects.filter(visible=True).order_by('-fecha_fin') if incluir_edu else []
    
    # Nota: Los cursos suelen ir atados a la educación, mantenemos esa lógica
    cursos_lista = CursoCapacitacion.objects.filter(visible=True).order_by('-fecha_fin') if incluir_edu else []
    
    reconocimientos = Reconocimiento.objects.filter(visible=True).order_by('-fecha') if incluir_rec else []
    
    proyectos = ProductoLaboral.objects.filter(visible=True).order_by('-fecha') if incluir_pro else []
    
    ventas = VentaGarage.objects.filter(activo=True).order_by('-fecha_publicacion') if incluir_ven else []
    
    academicos = ProductoAcademico.objects.filter(visible=True) if incluir_aca else []

    # 3. GENERACIÓN DEL PDF
    pdf_writer = PdfWriter()
    template = get_template('curriculum/cv_pdf.html') 

    def render_part(mode, extra={}):
        ctx = {'perfil': perfil, 'MEDIA_URL': settings.MEDIA_URL, 'section_mode': mode, 'styles': styles}
        ctx.update(extra)
        html = template.render(ctx)
        buf = BytesIO()
        pisa.CreatePDF(html, dest=buf, link_callback=link_callback)
        buf.seek(0)
        for p in PdfReader(buf).pages: pdf_writer.add_page(p)

    # PARTE A: Experiencia y Estudios
    if incluir_exp or incluir_edu:
        render_part('top', {'experiencias': experiencias, 'estudios': estudios})
    else:
        # Si no hay exp ni edu, renderizamos solo cabecera (top) con listas vacías
        render_part('top', {'experiencias': [], 'estudios': []})
    
    # PARTE B: Cursos
    if cursos_lista: 
        render_part('courses_list', {'cursos': cursos_lista})
    
    # PARTE C: Otros Bloques (Ahora respetarán si las listas están vacías)
    if reconocimientos or proyectos or ventas or academicos: 
        render_part('bottom', {
            'reconocimientos': reconocimientos, 
            'proyectos': proyectos, 
            'ventas': ventas,
            'academicos': academicos
        })
        
    # PARTE D: Índice de Anexos

    if experiencias or cursos_lista or reconocimientos:
        render_part('certificates_index', {
            'cursos': cursos_lista, 
            'reconocimientos': reconocimientos,
            'experiencias': experiencias
        })
    # PARTE E: Adjuntar PDFs
    # Unimos todas las listas que pueden tener PDFs
    todos_los_items = list(experiencias) + list(cursos_lista) + list(reconocimientos)

    for item in todos_los_items:
        # Detectamos el campo dinámicamente:
        # 1. Intenta buscar 'certificado_pdf' (Cursos/Reconocimientos)
        # 2. Si no, intenta buscar 'certificado' (Experiencia)
        archivo = getattr(item, 'certificado_pdf', getattr(item, 'certificado', None))

        if archivo:
            try:
                url = archivo.url
                if not url.startswith('http'): url = request.build_absolute_uri(url)
                res = requests.get(url, timeout=15)
                if res.status_code == 200:
                    for p in PdfReader(BytesIO(res.content)).pages: pdf_writer.add_page(p)
            except Exception as e:
                print(f"Error adjuntando PDF: {e}")
                pass
    # Finalizar
    try: final_writer = numerar_paginas(pdf_writer)
    except: final_writer = pdf_writer
    
    out = BytesIO()
    final_writer.write(out)
    response = HttpResponse(out.getvalue(), content_type='application/pdf')
    name = "".join([c for c in (perfil.nombres if perfil else "CV") if c.isalnum()])
    response['Content-Disposition'] = f'inline; filename="CV_{name}.pdf"'
    return response