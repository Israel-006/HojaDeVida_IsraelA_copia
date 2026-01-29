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

# ... (tus comandos anteriores)

# Crear superusuario automáticamente
# Cambia 'admin' y 'mi_password_segura' por lo que tú quieras
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('gael07', 'delgadoalvarez544@gmail.com', '123456789') if not User.objects.filter(username='gael07').exists() else print('El usuario ya existe')" | python manage.py shell