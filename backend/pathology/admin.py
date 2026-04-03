from django.contrib import admin
from .models import PathologyReport, MolecularMarkers

class MolecularMarkersInline(admin.StackedInline):
    """Molecular markers shown as inline within Pathology Report"""
    model = MolecularMarkers
    can_delete = False
    verbose_name_plural = "Molecular Markers"
    fieldsets = (
        ('KRAS Status', {
            'fields': ('kras_mutation', 'kras_mutation_type')
        }),
        ('EGFR/HER2', {
            'fields': ('egfr_expression', 'her2_status')
        }),
        ('MSI/Mismatch Repair', {
            'fields': ('msi_status', 'mlh1', 'msh2', 'msh6', 'pms2')
        }),
        ('Other Markers', {
            'fields': ('p53_status', 'smad4_status')
        }),
        ('NGS Findings', {
            'fields': ('ngs_performed', 'ngs_findings')
        }),
        ('Comments', {
            'fields': ('comments',)
        }),
    )


@admin.register(PathologyReport)
class PathologyReportAdmin(admin.ModelAdmin):
    list_display = ['patient', 'report_date', 'specimen_type', 'diagnosis', 'tumor_size_cm', 'margin_status']
    list_filter = ['report_date', 'specimen_type', 'margin_status', 't_stage', 'n_stage']
    search_fields = ['patient__patient_id', 'patient__last_name', 'diagnosis__diagnosis_name']
    
    inlines = [MolecularMarkersInline]
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient', 'report_date', 'specimen_type')
        }),
        ('Diagnosis', {
            'fields': ('diagnosis', 'histological_type', 'diagnosis_notes', 'histological_type_other')
        }),
        ('Tumor Details', {
            'fields': ('tumor_size_cm', 'tumor_size_other_dimensions', 'number_of_tumors', 'differentiation')
        }),
        ('Margins', {
            'fields': ('margin_status', 'margin_distance_mm', 'closest_margin')
        }),
        ('Invasion', {
            'fields': ('microvascular_invasion', 'macrovascular_invasion', 'vascular_invasion_details',
                      'perineural_invasion', 'peritoneal_invasion')
        }),
        ('Lymph Nodes', {
            'fields': ('lymph_nodes_examined', 'lymph_nodes_positive', 'lymph_node_ratio', 'lymph_node_stations')
        }),
        ('TNM Staging (AJCC 8th)', {
            'fields': ('t_stage', 'n_stage', 'm_stage')
        }),
        ('Liver-Specific Findings', {
            'fields': ('background_liver', 'fibrosis_score', 'steatosis_percentage'),
            'classes': ('collapse',)
        }),
        ('Pancreas-Specific Findings', {
            'fields': ('pancreatic_parenchyma', 'pancreatic_intraepithelial_neoplasia'),
            'classes': ('collapse',)
        }),
    )
    
    # Audit fields if they exist
    if hasattr(PathologyReport, 'created_by'):
        exclude = ('created_by', 'updated_by')
        readonly_fields = ('created_at', 'updated_at')


# Optional: Register MolecularMarkers separately if you want to keep it visible,
# but it's now available as inline within PathologyReport
@admin.register(MolecularMarkers)
class MolecularMarkersAdmin(admin.ModelAdmin):
    """Separate admin for Molecular Markers (mostly for reference)"""
    list_display = ['pathology_report']
    search_fields = ['pathology_report__patient__patient_id']
    
    # Hide from main admin menu to avoid duplication (optional)
    def has_module_permission(self, request):
        return False
