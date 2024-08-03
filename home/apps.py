from django.apps import AppConfig

class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'  # Ensure this matches the Python path to your app

    def ready(self):
        # This is where you import your signals
        # It ensures signals are connected when the app is ready
        import home.signals  # Adjust the import path if your app's structure is different
