from django.contrib import admin
from .models import (
    SurgicalProcedure, 
    ChemotherapyProtocol, 
    FollowUp, 
    LiverResectionDetail, 
    PancreaticResectionDetail, 
    BiliaryProcedureDetail,
    LiverTumor,
    TextbookOutcome,
)

# Liver Tumor Inline (for LiverResectionDetail)
class LiverTumorInline(admin.TabularInline):
    model = LiverTumor
    extra = 1
    fields = ['segment', 'segment_details', 'size_cm', 'size_other_dimensions', 
              'is_primary', 'differentiation', 'microvascular_invasion', 
              'macrovascular_invasion', 'necrosis_percentage']
    show_change_link = True


# Inline for LiverResectionDetail (to show inside SurgicalProcedure)
class LiverResectionDetailInline(admin.StackedInline):
    model = LiverResectionDetail
    can_delete = False
    verbose_name_plural = "Liver Resection Details"
    fieldsets = (
        ('Resection Details', {
            'fields': ('resection_type', 'hepatectomy_type', 'number_of_segments')
        }),
        ('Segments Resected', {
            'fields': ('segment_1', 'segment_2', 'segment_3', 'segment_4a', 'segment_4b',
                      'segment_5', 'segment_6', 'segment_7', 'segment_8'),
        }),
        ('Tumor Information', {
            'fields': ('total_tumor_count', 'largest_tumor_size_cm', 'total_tumor_volume_cc')
        }),
        ('Margins', {
            'fields': ('margin_status', 'margin_distance_mm'),
        }),
        ('Parenchymal Quality', {
            'fields': ('parenchyma_quality', 'flr_percentage', 'flr_volume_cc'),
        }),
        ('Vascular Reconstruction', {
            'fields': ('portal_vein_reconstruction', 'hepatic_artery_reconstruction', 
                      'hepatic_vein_reconstruction', 'ivc_resection'),
        }),
    )
    
    # Add LiverTumor inline inside LiverResectionDetail
    inlines = [LiverTumorInline]


# Inline for PancreaticResectionDetail
class PancreaticResectionDetailInline(admin.StackedInline):
    model = PancreaticResectionDetail
    can_delete = False
    verbose_name_plural = "Pancreatic Resection Details"
    fieldsets = (
        ('Resection Details', {
            'fields': ('pancreatectomy_variant', 'tumor_location', 'tumor_size_cm')
        }),
        ('Pancreatic Duct', {
            'fields': ('pancreatic_duct_dilated', 'pancreatic_duct_size_mm', 'pancreatic_duct_stent'),
        }),
        ('Vascular Involvement', {
            'fields': ('portal_vein_invasion', 'portal_vein_resection', 'portal_vein_reconstruction_type',
                      'superior_mesenteric_vein_invasion', 'superior_mesenteric_artery_invasion',
                      'celiac_axis_invasion', 'hepatic_artery_invasion'),
        }),
        ('Pancreatic Anastomosis', {
            'fields': ('pancreatic_texture', 'anastomosis_type', 'pancreatic_jejunostomy', 'pancreatic_gastrostomy'),
        }),
        ('Drain', {
            'fields': ('external_drain_placed', 'drain_amylase_pod1', 'drain_amylase_pod3', 'drain_removal_day'),
        }),
    )


# Inline for BiliaryProcedureDetail
class BiliaryProcedureDetailInline(admin.StackedInline):
    model = BiliaryProcedureDetail
    can_delete = False
    verbose_name_plural = "Biliary Procedure Details"
    fieldsets = (
        ('Procedure Details', {
            'fields': ('biliary_procedure', 'bismuth_classification')
        }),
        ('Bile Duct', {
            'fields': ('bile_duct_diameter_mm', 'bile_duct_stricture', 'stricture_location'),
        }),
        ('Anastomosis', {
            'fields': ('anastomosis_level', 'number_of_anastomoses'),
        }),
        ('Stents', {
            'fields': ('preoperative_stent', 'preoperative_stent_type', 'postoperative_stent'),
        }),
        ('Bile Leak Management', {
            'fields': ('bile_leak_management', 'ercp_performed', 'ptbd_performed'),
        }),
    )


#@admin.register(LiverResectionDetail)
#class LiverResectionDetailAdmin(admin.ModelAdmin):
#    list_display = ['surgical_procedure', 'get_patient', 'hepatectomy_type', 'total_tumor_count', 'largest_tumor_size_cm']
#    search_fields = ['surgical_procedure__patient__patient_id']
#    inlines = [LiverTumorInline]
#    
#    def get_patient(self, obj):
#        return obj.surgical_procedure.patient
#    get_patient.short_description = 'Patient'


@admin.register(SurgicalProcedure)
class SurgicalProcedureAdmin(admin.ModelAdmin):
    list_display = ['patient', 'procedure_date', 'procedure_type', 'primary_surgeon', 'surgical_approach', 'operative_time_minutes']
    list_filter = ['procedure_type', 'procedure_date', 'surgical_approach', 'urgency', 'indication']
    
    search_fields = [
        'patient__patient_id', 
        'patient__last_name', 
        'primary_surgeon__username', 
        'primary_surgeon__first_name',
        'primary_surgeon__last_name',
        'assistant_surgeon_1__username',
        'assistant_surgeon_1__first_name',
        'assistant_surgeon_1__last_name',
        'assistant_surgeon_2__username',
        'assistant_surgeon_2__first_name',
        'assistant_surgeon_2__last_name',
        'supervising_surgeon__username',
        'supervising_surgeon__first_name',
        'supervising_surgeon__last_name',
        'anesthesiologist__username',
        'anesthesiologist__first_name',
        'anesthesiologist__last_name',
    ]
    
    inlines = [
        LiverResectionDetailInline,
        PancreaticResectionDetailInline,
        BiliaryProcedureDetailInline,
    ]
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient',)
        }),
        ('Procedure Details', {
            'fields': ('procedure_date', 'procedure_type', 'surgical_approach',
                       'liver_surgery_subtype', 'pancreatic_surgery_subtype', 'biliary_surgery_subtype')
        }),
        ('Surgical Team', {
            'fields': ('primary_surgeon', 'assistant_surgeon_1', 'assistant_surgeon_2', 
                      'supervising_surgeon', 'anesthesiologist'),
            'description': 'Select the surgical team members'
        }),
        ('Indication & Urgency', {
            'fields': ('urgency', 'indication', 'indication_other'),
            'classes': ('collapse',)
        }),
        ('Neoadjuvant Therapy', {
            'fields': ('neoadjuvant_chemotherapy', 'neoadjuvant_radiotherapy', 'neoadjuvant_chemoradiation',
                      'neoadjuvant_protocol', 'days_from_neoadjuvant_to_surgery'),
            'classes': ('collapse',)
        }),
        ('Operative Details', {
            'fields': ('operative_time_minutes', 'blood_loss_ml', 'intraoperative_transfusion', 'transfusion_units',
                      'intraoperative_complications', 'conversion_to_open', 'conversion_reason')
        }),
        ('Pringle Maneuver', {
            'fields': ('pringle_maneuver', 'pringle_time_minutes', 'pringle_cycles'),
            'classes': ('collapse',)
        }),
        ('Postoperative Course', {
            'fields': ('hospital_stay_days', 'icu_stay_days', 'enhanced_recovery_protocol')
        }),
        ('Complications & Outcomes', {
            'fields': ('clavien_dindo_grade',)
        }),
        ('Readmission & Mortality', {
            'fields': ('readmission_30d', 'readmission_90d', 'readmission_reason',
                      'mortality_30d', 'mortality_90d', 'mortality_in_hospital', 'date_of_death_if_known'),
            'classes': ('collapse',)
        }),
        ('Quality Metrics', {
            'fields': ('operative_report_available', 'operative_report_link'),
            'classes': ('collapse',)
        }),
    )
    
    # Hide audit fields
    exclude = ('created_by', 'updated_by')
    readonly_fields = ('created_at', 'updated_at')


#@admin.register(PancreaticResectionDetail)
#class PancreaticResectionDetailAdmin(admin.ModelAdmin):
#    list_display = ['surgical_procedure', 'get_patient', 'pancreatectomy_variant', 'tumor_location']
#    search_fields = ['surgical_procedure__patient__patient_id']
#    
#    def get_patient(self, obj):
#        return obj.surgical_procedure.patient
#    get_patient.short_description = 'Patient'
#
#
#@admin.register(BiliaryProcedureDetail)
#class BiliaryProcedureDetailAdmin(admin.ModelAdmin):
#    list_display = ['surgical_procedure', 'get_patient', 'biliary_procedure', 'bismuth_classification']
#    search_fields = ['surgical_procedure__patient__patient_id']
#    
#    def get_patient(self, obj):
#        return obj.surgical_procedure.patient
#    get_patient.short_description = 'Patient'


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
    
    exclude = ('created_by', 'updated_by')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TextbookOutcome)
class TextbookOutcomeAdmin(admin.ModelAdmin):
    list_display = ['surgical_procedure', 'achieved', 'no_major_complications', 'no_prolonged_los', 
                   'no_readmission', 'no_mortality', 'negative_margins']
    list_filter = ['no_major_complications', 'no_prolonged_los', 'no_readmission', 'no_mortality', 
                  'negative_margins', 'adequate_lymph_node_yield']
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
        return '✓' if obj.achieved else '✗'
    achieved.short_description = 'Achieved'
    achieved.boolean = True
