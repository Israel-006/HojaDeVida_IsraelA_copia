#!/usr/bin/env bash
# Salir si hay un error
set -o errexit

# 1. Limpieza profunda
rm -rf staticfiles

# 2. Instalar librerías
pip install -r requirements.txt

# 3. Archivos estáticos
python manage.py collectstatic --no-input --clear

# 4. Migraciones de base de datos
python manage.py migrate

# 5. SUPERUSUARIO (Lógica corregida: Fuerza la actualización)
# Este script busca al usuario 'gael06'. Si no existe, lo crea.
# Si ya existe, LE CAMBIA LA CONTRASEÑA a '123456789' obligatoriamente.
echo "
import os
import django
from django.contrib.auth import get_user_model

# Configuración inicial para scripts externos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hoja_de_vida.settings')
django.setup()

User = get_user_model()
username = 'gael06'
email = 'delgadoalvarez544@gmail.com'
password = '123456789'

try:
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    action = 'creado' if created else 'actualizado'
    print(f'✅ ÉXITO: Usuario {username} {action} con contraseña corregida.')
except Exception as e:
    print(f'❌ ERROR: {e}')
" | python manage.py shell