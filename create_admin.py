import os
import django

# Configura Django para que este script pueda hablar con la base de datos
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hoja_de_vida.settings")
django.setup()

from django.contrib.auth import get_user_model

def reset_password():
    User = get_user_model()
    username = 'gael06'
    password = '123456789'
    email = 'delgadoalvarez544@gmail.com'

    print("--- INICIANDO PROCESO DE SUPERUSUARIO ---")
    
    # Busca al usuario o lo crea si no existe
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    
    # SIEMPRE resetea la contraseña y los permisos, exista o no
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    
    if created:
        print(f"✅ Usuario {username} CREADO exitosamente.")
    else:
        print(f"✅ Usuario {username} ACTUALIZADO (Contraseña reseteada).")

if __name__ == "__main__":
    reset_password()