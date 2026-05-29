from django.apps import AppConfig


class FinanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.finance"
    verbose_name = "Finanse"

    def ready(self) -> None:
        # rejestracja sygnalow (events)
        from . import signals  # noqa: F401
