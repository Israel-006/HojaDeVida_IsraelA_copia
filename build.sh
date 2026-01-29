#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instalar requerimientos
pip install -r requirements.txt

# 2. Archivos estáticos
rm -rf staticfiles
python manage.py collectstatic --no-input --clear

# 3. Migraciones
python manage.py migrate

# 4. EJECUTAR EL SCRIPT DE ADMIN (Aquí está la magia)
python create_admin.py