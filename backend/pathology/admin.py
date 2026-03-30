from django.contrib import admin
from .models import PathologyReport, MolecularMarkers

class MolecularMarkersInline(admin.StackedInline):
    model = MolecularMarkers
    can_delete = False
    verbose_name_plural = "Molecular Markers"
    extra = 1

@admin.register(PathologyReport)
class PathologyReportAdmin(admin.ModelAdmin):
    list_display = ['patient', 'report_date', 'get_diagnosis', 'tumor_size_cm']
    list_filter = ['report_date', 'specimen_type']
    search_fields = ['patient__patient_id', 'patient__last_name']
    inlines = [MolecularMarkersInline]
    
    def get_diagnosis(self, obj):
        if obj.diagnosis:
            return f"{obj.diagnosis.icd10_code} - {obj.diagnosis.diagnosis_name}"
        return "-"
    get_diagnosis.short_description = 'Diagnosis'

@admin.register(MolecularMarkers)
class MolecularMarkersAdmin(admin.ModelAdmin):
    list_display = ['pathology_report', 'kras_mutation', 'msi_status']
    search_fields = ['pathology_report__patient__patient_id']
