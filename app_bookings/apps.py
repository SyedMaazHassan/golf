from django.apps import AppConfig


class AppBookingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_bookings'

    def ready(self):
        import app_bookings.signals
