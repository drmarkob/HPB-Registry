from django.contrib import admin
from .models import Diagnosis, HistologyType

@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ['icd10_code', 'diagnosis_name', 'category']
    list_filter = ['category']
    search_fields = ['icd10_code', 'diagnosis_name']

@admin.register(HistologyType)
class HistologyTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'organ_system']
    list_filter = ['category', 'organ_system']
    search_fields = ['name']
