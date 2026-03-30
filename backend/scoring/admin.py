from django.contrib import admin
from .models import MELDScore, ASAScore, ChildPughScore, CharlsonComorbidity

@admin.register(MELDScore)
class MELDScoreAdmin(admin.ModelAdmin):
    list_display = ['patient', 'date_assessed', 'score']
    list_filter = ['date_assessed']
    search_fields = ['patient__patient_id', 'patient__last_name']

@admin.register(ASAScore)
class ASAScoreAdmin(admin.ModelAdmin):
    list_display = ['patient', 'date_assessed', 'asa_class']
    list_filter = ['date_assessed']
    search_fields = ['patient__patient_id', 'patient__last_name']

@admin.register(ChildPughScore)
class ChildPughScoreAdmin(admin.ModelAdmin):
    list_display = ['patient', 'date_assessed', 'score', 'class_grade']
    list_filter = ['date_assessed']
    search_fields = ['patient__patient_id', 'patient__last_name']

@admin.register(CharlsonComorbidity)
class CharlsonComorbidityAdmin(admin.ModelAdmin):
    list_display = ['patient', 'date_assessed', 'score']
    list_filter = ['date_assessed']
    search_fields = ['patient__patient_id', 'patient__last_name']
