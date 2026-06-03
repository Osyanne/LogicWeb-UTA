from django.core.management.base import BaseCommand

from apps.ejercicios.models import Usuario, Ejercicio, Intento

DEMO_USERNAME = 'demo'
DEMO_PASSWORD = 'Demo123*'


class Command(BaseCommand):
    help = 'Crea (idempotente) la cuenta demo de estudiante y le siembra algo de progreso.'

    def handle(self, *args, **options):
        usuario, creado = Usuario.objects.get_or_create(
            username=DEMO_USERNAME,
            defaults={
                'first_name': 'Estudiante',
                'last_name': 'Demo',
                'email': 'demo@uta.edu.ec',
                'rol': 'estudiante',
            },
        )
        if creado:
            usuario.set_password(DEMO_PASSWORD)
            usuario.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS(f'Cuenta demo creada: {DEMO_USERNAME}'))
        else:
            if not usuario.check_password(DEMO_PASSWORD):
                usuario.set_password(DEMO_PASSWORD)
                usuario.save(update_fields=['password'])
                self.stdout.write(self.style.WARNING('Contraseña demo re-sincronizada.'))
            self.stdout.write(f'Cuenta demo ya existe: {DEMO_USERNAME}')

        # Siembra de progreso: solo si el demo aún no tiene intentos (idempotente).
        if usuario.intentos.filter(resultado='correcto').exists():
            self.stdout.write('El demo ya tiene intentos correctos; no se siembra de nuevo.')
            return

        ejercicios = list(Ejercicio.objects.filter(activo=True)[:5])
        if not ejercicios:
            self.stdout.write(self.style.WARNING('No hay ejercicios; se omite la siembra de progreso.'))
            return

        for ej in ejercicios:
            Intento.objects.create(
                usuario=usuario,
                ejercicio=ej,
                respuesta_usuario=ej.solucion_esperada or 'demo',
                resultado='correcto',
            )
        self.stdout.write(self.style.SUCCESS(
            f'Sembrados {len(ejercicios)} intentos correctos (el signal actualizó ProgresoEstudiante).'
        ))
