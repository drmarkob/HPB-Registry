from django.contrib import admin
from .models import (
    SurgicalProcedure, 
    ChemotherapyProtocol, 
    FollowUp, 
    LiverResectionDetail, 
    PancreaticResectionDetail, 
    BiliaryProcedureDetail,
    LiverTumor,
    TextbookOutcome,  # Add this line
)

# Add this inline class before LiverResectionDetailAdmin
class LiverTumorInline(admin.TabularInline):
    model = LiverTumor
    extra = 1
    fields = ['segment', 'segment_details', 'size_cm', 'size_other_dimensions', 
              'is_primary', 'differentiation', 'microvascular_invasion', 
              'macrovascular_invasion', 'necrosis_percentage']
    show_change_link = True

@admin.register(LiverResectionDetail)
class LiverResectionDetailAdmin(admin.ModelAdmin):
    list_display = ['surgical_procedure', 'get_patient', 'hepatectomy_type', 'total_tumor_count', 'largest_tumor_size_cm']
    search_fields = ['surgical_procedure__patient__patient_id']
    
    def get_patient(self, obj):
        return obj.surgical_procedure.patient
    get_patient.short_description = 'Patient'
    
    inlines = [LiverTumorInline]
    
    fieldsets = (
        ('Resection Details', {
            'fields': ('resection_type', 'hepatectomy_type', 'number_of_segments')
        }),
        ('Segments Resected', {
            'fields': ('segment_1', 'segment_2', 'segment_3', 'segment_4a', 'segment_4b',
                      'segment_5', 'segment_6', 'segment_7', 'segment_8'),
            'classes': ('collapse',)
        }),
        ('Tumor Information', {
            'fields': ('total_tumor_count', 'largest_tumor_size_cm', 'total_tumor_volume_cc')
        }),
        ('Margins', {
            'fields': ('margin_status', 'margin_distance_mm'),
            'classes': ('collapse',)
        }),
        ('Parenchymal Quality', {
            'fields': ('parenchyma_quality', 'flr_percentage', 'flr_volume_cc'),
            'classes': ('collapse',)
        }),
        ('Vascular Reconstruction', {
            'fields': ('portal_vein_reconstruction', 'hepatic_artery_reconstruction', 
                      'hepatic_vein_reconstruction', 'ivc_resection'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SurgicalProcedure)
class SurgicalProcedureAdmin(admin.ModelAdmin):
    list_display = ['patient', 'procedure_date', 'procedure_type', 'surgical_approach', 'operative_time_minutes']
    list_filter = ['procedure_type', 'procedure_date', 'surgical_approach']
    search_fields = ['patient__patient_id', 'patient__last_name']
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient',)
        }),
        ('Procedure Details', {
            'fields': ('procedure_date', 'procedure_type', 'surgical_approach',
                      'liver_surgery_subtype', 'pancreatic_surgery_subtype', 'biliary_surgery_subtype')
        }),
        ('Operative Details', {
            'fields': ('operative_time_minutes', 'blood_loss_ml', 'intraoperative_transfusion', 'transfusion_units')
        }),
        ('Pringle Maneuver', {
            'fields': ('pringle_maneuver', 'pringle_time_minutes', 'pringle_cycles'),
            'classes': ('collapse',)
        }),
        ('Hospital Course', {
            'fields': ('hospital_stay_days', 'icu_stay_days', 'readmission_30d', 'readmission_reason'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PancreaticResectionDetail)
class PancreaticResectionDetailAdmin(admin.ModelAdmin):
    list_display = ['surgical_procedure', 'get_patient', 'pancreatectomy_variant', 'tumor_location']
    search_fields = ['surgical_procedure__patient__patient_id']
    
    def get_patient(self, obj):
        return obj.surgical_procedure.patient
    get_patient.short_description = 'Patient'

@admin.register(BiliaryProcedureDetail)
class BiliaryProcedureDetailAdmin(admin.ModelAdmin):
    list_display = ['surgical_procedure', 'get_patient', 'biliary_procedure', 'bismuth_classification']
    search_fields = ['surgical_procedure__patient__patient_id']
    
    def get_patient(self, obj):
        return obj.surgical_procedure.patient
    get_patient.short_description = 'Patient'

@admin.register(ChemotherapyProtocol)
class ChemotherapyProtocolAdmin(admin.ModelAdmin):
    list_display = ['patient', 'start_date', 'protocol', 'cycles_completed']
    list_filter = ['protocol', 'setting']
    search_fields = ['patient__patient_id', 'patient__last_name']

@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ['patient', 'followup_date', 'alive', 'recurrence']
    list_filter = ['followup_date', 'alive', 'recurrence']
    search_fields = ['patient__patient_id', 'patient__last_name']

@admin.register(TextbookOutcome)
class TextbookOutcomeAdmin(admin.ModelAdmin):
    list_display = ['surgical_procedure', 'achieved', 'no_major_complications', 'no_prolonged_los', 
                   'no_readmission', 'no_mortality', 'negative_margins']
    list_filter = ['no_major_complications', 'no_prolonged_los', 'no_readmission', 'no_mortality', 
                  'negative_margins', 'adequate_lymph_node_yield']  # Removed 'achieved' from list_filter
    search_fields = ['surgical_procedure__patient__patient_id', 'surgical_procedure__patient__first_name']
    readonly_fields = ['calculated_at']
    
    fieldsets = (
        ('Surgical Procedure', {
            'fields': ('surgical_procedure',)
        }),
        ('Textbook Outcome Components', {
            'fields': ('no_major_complications', 'no_prolonged_los', 'no_readmission', 
                      'no_mortality', 'negative_margins', 'adequate_lymph_node_yield')
        }),
        ('System Fields', {
            'fields': ('calculated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def achieved(self, obj):
        """Display if textbook outcome was achieved"""
        return '✓' if obj.achieved else '✗'
    achieved.short_description = 'Achieved'
    achieved.boolean = True
