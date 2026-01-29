#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instalar requerimientos
pip install -r requirements.txt

# 2. Archivos estaticos
rm -rf staticfiles
python manage.py collectstatic --no-input --clear

# 3. Migraciones
python manage.py migrate

# 4. SUPERUSUARIO (Version INFALIBLE - Solo texto simple)
# Este script se ejecuta directo en la shell. Si falla, lo veremos en el log.
echo "
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hoja_de_vida.settings')
django.setup()

User = get_user_model()
username = 'admin_final'
email = 'admin@example.com'
password = '123456789'

print('--- STARTING SUPERUSER CHECK ---')
try:
    if User.objects.filter(username=username).exists():
        print('User exists. Resetting password...')
        u = User.objects.get(username=username)
        u.set_password(password)
        u.is_superuser = True
        u.is_staff = True
        u.save()
        print('PASSWORD RESET SUCCESS')
    else:
        print('Creating new user...')
        User.objects.create_superuser(username, email, password)
        print('USER CREATED SUCCESS')
except Exception as e:
    print(f'ERROR: {e}')
print('--- END SUPERUSER CHECK ---')
" | python manage.py shell