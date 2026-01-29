#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Limpieza profunda (Clave del archivo funcional)
rm -rf staticfiles

# 2. Instalar requerimientos
pip install -r requirements.txt

# 3. Colectar estáticos limpiando caché previa
python manage.py collectstatic --no-input --clear

# 4. Migraciones
python manage.py migrate