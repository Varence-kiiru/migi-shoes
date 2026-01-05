from django.apps import AppConfig


class ModelsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'models_app'

    def ready(self):
        # Import signal handlers to register them
        try:
            from . import signals  # noqa: F401
        except Exception:
            # keep startup resilient; actual errors will surface in runtime checks
            pass
