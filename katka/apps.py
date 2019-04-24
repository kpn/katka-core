from django.apps import AppConfig


class KatkaCoreConfig(AppConfig):
    name = 'katka'
    label = 'katka'

    def ready(self):
        super().ready()
        # import signals so the signal handlers are registered
        from . import signals  # noqa: F401
