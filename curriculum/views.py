import os
from io import BytesIO
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import (
    DatosPersonales, ExperienciaLaboral, EstudioRealizado, 
    CursoCapacitacion, Reconocimiento, ProductoLaboral, VentaGarage
)
from pypdf import PdfWriter, PdfReader

def link_callback(uri, rel):
    sUrl = settings.STATIC_URL
    sRoot = settings.STATIC_ROOT
    mUrl = settings.MEDIA_URL
    mRoot = settings.MEDIA_ROOT

    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri

    if not os.path.isfile(path):
        return uri
    return path

# ==========================================
# VISTAS DE LA PÁGINA WEB (CORREGIDAS)
# ==========================================

def inicio(request):
    perfil = DatosPersonales.objects.first()
    return render(request, 'curriculum/inicio.html', {'perfil': perfil})

def perfil(request):
    perfil = DatosPersonales.objects.first()
    return render(request, 'curriculum/datos_personales.html', {'perfil': perfil})

def experiencia(request):
    perfil = DatosPersonales.objects.first()
    # Orden descendente por ID (Lo último agregado primero)
    experiencias = ExperienciaLaboral.objects.all().order_by('-id')
    return render(request, 'curriculum/experiencia.html', {'perfil': perfil, 'experiencias': experiencias})

def educacion(request):
    perfil = DatosPersonales.objects.first()
    estudios = EstudioRealizado.objects.all().order_by('-id')
    # CORREGIDO: La clave ahora es 'educacion' para coincidir con el HTML {% for edu in educacion %}
    return render(request, 'curriculum/educacion.html', {'perfil': perfil, 'educacion': estudios})

def cursos(request):
    perfil = DatosPersonales.objects.first()
    cursos = CursoCapacitacion.objects.all().order_by('-id')
    return render(request, 'curriculum/cursos.html', {'perfil': perfil, 'cursos': cursos})

def reconocimientos(request):
    perfil = DatosPersonales.objects.first()
    reconocimientos = Reconocimiento.objects.all().order_by('-id')
    return render(request, 'curriculum/reconocimientos.html', {'perfil': perfil, 'reconocimientos': reconocimientos})

def trabajos(request):
    perfil = DatosPersonales.objects.first()
    proyectos = ProductoLaboral.objects.all().order_by('-id')
    # CORREGIDO: La clave es 'trabajos' para coincidir con {% for trabajo in trabajos %}
    return render(request, 'curriculum/proyectos.html', {'perfil': perfil, 'trabajos': proyectos})

def venta(request):
    perfil = DatosPersonales.objects.first()
    productos = VentaGarage.objects.all().order_by('-id')
    # CORREGIDO: La clave es 'servicios' para coincidir con {% for item in servicios %}
    return render(request, 'curriculum/venta.html', {'perfil': perfil, 'servicios': productos})

def contacto(request):
    perfil = DatosPersonales.objects.first()
    return render(request, 'curriculum/contacto.html', {'perfil': perfil})


# ==========================================
# GENERADOR DE PDF
# ==========================================
def generar_cv(request):
    perfil = DatosPersonales.objects.first()
    
    # 1. VERIFICAR EL ORIGEN
    if request.GET.get('origen') == 'personalizado':
        incluir_exp = request.GET.get('experiencia') == 'on'
        incluir_edu = request.GET.get('educacion') == 'on'
        incluir_rec = request.GET.get('reconocimientos') == 'on'
        incluir_pro = request.GET.get('proyectos') == 'on'
        incluir_ven = request.GET.get('venta') == 'on'
    else:
        incluir_exp = True
        incluir_edu = True
        incluir_rec = True
        incluir_pro = True
        incluir_ven = True

    # 2. FILTRAR DATOS
    experiencias = ExperienciaLaboral.objects.all().order_by('-id') if incluir_exp else []
    estudios = EstudioRealizado.objects.all().order_by('-id') if incluir_edu else []
    cursos_lista = CursoCapacitacion.objects.all().order_by('-id') if incluir_edu else []
    reconocimientos = Reconocimiento.objects.all().order_by('-id') if incluir_rec else []
    proyectos = ProductoLaboral.objects.all().order_by('-id') if incluir_pro else []
    ventas = VentaGarage.objects.all().order_by('-id') if incluir_ven else []

    pdf_writer = PdfWriter()
    template = get_template('curriculum/cv_pdf.html') 

    # PASO 1: PARTE SUPERIOR
    context_part1 = {
        'perfil': perfil,
        'experiencias': experiencias,
        'estudios': estudios,
        'cursos': [], 
        'reconocimientos': [],
        'proyectos': [],
        'ventas': [],
        'section_mode': 'top',
        'MEDIA_URL': settings.MEDIA_URL,
    }
    
    html_1 = template.render(context_part1)
    buffer_1 = BytesIO()
    pisa.CreatePDF(html_1, dest=buffer_1, link_callback=link_callback)
    buffer_1.seek(0)
    reader_1 = PdfReader(buffer_1)
    for page in reader_1.pages:
        pdf_writer.add_page(page)

    # PASO 2: CURSOS INTERCALADOS
    if cursos_lista:
        for curso in cursos_lista:
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

            if curso.certificado_pdf:
                try:
                    pdf_path = curso.certificado_pdf.path
                    if os.path.exists(pdf_path):
                        reader_cert = PdfReader(pdf_path)
                        for page in reader_cert.pages:
                            pdf_writer.add_page(page)
                except Exception as e:
                    print(f"Error adjuntando certificado: {e}")

    # PASO 3: PARTE INFERIOR
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

    final_buffer = BytesIO()
    pdf_writer.write(final_buffer)
    
    response = HttpResponse(final_buffer.getvalue(), content_type='application/pdf')
    filename = f"CV_Personalizado_{perfil.nombres}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response