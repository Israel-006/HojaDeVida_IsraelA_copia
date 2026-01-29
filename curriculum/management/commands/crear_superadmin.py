from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Crea un superusuario de manera segura en Render'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'admin_final'
        email = 'tu_email@gmail.com'
        password = '123456789' # <--- ESTA SERÁ TU CONTRASEÑA

        self.stdout.write(f"--- INTENTANDO GESTIONAR USUARIO {username} ---")

        try:
            user, created = User.objects.get_or_create(username=username, defaults={'email': email})
            
            # Forzamos la contraseña SIEMPRE
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.save()

            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Usuario {username} CREADO correctamente."))
            else:
                self.stdout.write(self.style.SUCCESS(f"✅ Usuario {username} ACTUALIZADO (Contraseña reseteada)."))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ ERROR CRÍTICO: {e}"))