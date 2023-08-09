from django.apps import AppConfig


class SummarizationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "summarizations"
    verbose_name = "Суммаризация"

    def ready(self):
        import summarizations.signals
