# curriculum/cv_settings.py

DEFAULT_SETTINGS = {
    'name_color': '#1a1a1a',        # NUEVO: Color solo para Nombres
    'surname_color': '#5A7D84',     # NUEVO: Color solo para Apellidos
    'header_color': '#1a1a1a',      # Color para Títulos de Secciones
    'accent_color': '#5A7D84',      # Subtítulos y detalles
    'line_color': '#BBD2D6',        # Líneas
    'font_family': 'Helvetica',
    'show_photo': True,
}

def get_cv_styles(request):
    if request.GET.get('origen') != 'personalizado':
        return DEFAULT_SETTINGS

    font_map = {
        'helvetica': 'Helvetica, Arial, sans-serif',
        'times': 'Times-Roman, Times New Roman, serif',
        'courier': 'Courier, monospace',
    }
    
    selected_font = request.GET.get('font_family', 'helvetica')

    return {
        'name_color': request.GET.get('name_color', DEFAULT_SETTINGS['name_color']),
        'surname_color': request.GET.get('surname_color', DEFAULT_SETTINGS['surname_color']),
        'header_color': request.GET.get('header_color', DEFAULT_SETTINGS['header_color']),
        'accent_color': request.GET.get('accent_color', DEFAULT_SETTINGS['accent_color']),
        'line_color': request.GET.get('line_color', DEFAULT_SETTINGS['line_color']),
        'font_family': font_map.get(selected_font, font_map['helvetica']),
        'show_photo': request.GET.get('show_photo') == 'on'
    }