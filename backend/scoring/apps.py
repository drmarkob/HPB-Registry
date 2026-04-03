from django.apps import AppConfig


class ScoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scoring'
    verbose_name = 'Clinical Scoring Systems'
    
    def ready(self):
        # Import signals if we add them later
        pass
