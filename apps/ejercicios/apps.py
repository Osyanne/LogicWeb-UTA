from django.apps import AppConfig


class EjerciciosConfig(AppConfig):
    name = 'apps.ejercicios'

    def ready(self):
        import apps.ejercicios.signals  # noqa: F401 — registra los signals
