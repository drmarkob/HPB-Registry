from django.apps import AppConfig

class HpbRegistryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hpb_registry'
    
    def ready(self):
        # Import admin to ensure it's loaded
        import hpb_registry.admin
