from django.contrib import admin
from .models import LaboratoryPanel, TumorMarkerPanel, MicrobiologyCulture

@admin.register(LaboratoryPanel)
class LaboratoryPanelAdmin(admin.ModelAdmin):
    list_display = ['patient', 'collection_date', 'timing', 'hemoglobin', 'wbc', 'crp']
    list_filter = ['collection_date', 'timing']
    search_fields = ['patient__patient_id', 'patient__last_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('patient', 'collection_date', 'collection_time', 'timing')
        }),
        ('Complete Blood Count', {
            'fields': ('hemoglobin', 'hematocrit', 'wbc', 'neutrophils', 'lymphocytes', 'monocytes', 'platelets'),
        }),
        ('Biochemistry', {
            'fields': ('total_protein', 'albumin', 'urea', 'creatinine', 'egfr'),
            'classes': ('collapse',)
        }),
        ('Liver Function Tests', {
            'fields': ('alt', 'ast', 'alp', 'ggt', 'total_bilirubin', 'direct_bilirubin', 'indirect_bilirubin'),
            'classes': ('collapse',)
        }),
        ('Coagulation', {
            'fields': ('inr', 'pt', 'ptt'),
            'classes': ('collapse',)
        }),
        ('Electrolytes', {
            'fields': ('sodium', 'potassium', 'chloride', 'calcium', 'magnesium', 'phosphate'),
            'classes': ('collapse',)
        }),
        ('Inflammatory Markers', {
            'fields': ('crp', 'esr', 'procalcitonin'),
            'classes': ('collapse',)
        }),
        ('Nutritional Markers', {
            'fields': ('prealbumin', 'transferrin'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('comments',),
            'classes': ('collapse',)
        }),
    )

@admin.register(TumorMarkerPanel)
class TumorMarkerPanelAdmin(admin.ModelAdmin):
    list_display = ['patient', 'collection_date', 'timing', 'ca19_9', 'cea', 'afp']
    list_filter = ['collection_date', 'timing']
    search_fields = ['patient__patient_id', 'patient__last_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('patient', 'collection_date', 'timing')
        }),
        ('Common HPB Markers', {
            'fields': ('ca19_9', 'cea', 'afp'),
        }),
        ('Pancreatic Neuroendocrine Markers', {
            'fields': ('chromogranin_a', 'neuron_specific_enolase', 'pancreastatin', 'serotonin', 'hiaa_5'),
            'classes': ('collapse',),
        }),
        ('Biliary Tract Markers', {
            'fields': ('ca_50', 'ca_242'),
            'classes': ('collapse',),
        }),
        ('Other Markers', {
            'fields': ('ca_125', 'ca_15_3', 'ca_72_4'),
            'classes': ('collapse',),
        }),
        ('Liver-Specific Markers', {
            'fields': ('des_gamma_carboxy_prothrombin', 'golgi_protein_73'),
            'classes': ('collapse',),
        }),
        ('Notes', {
            'fields': ('notes',),
        }),
    )

@admin.register(MicrobiologyCulture)
class MicrobiologyCultureAdmin(admin.ModelAdmin):
    list_display = ['patient', 'collection_date', 'specimen_type', 'organism']
    list_filter = ['collection_date', 'specimen_type']
    search_fields = ['patient__patient_id', 'patient__last_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('patient', 'collection_date', 'specimen_type')
        }),
        ('Microbiology Results', {
            'fields': ('organism', 'antibiotic_sensitivity', 'resistant_antibiotics')
        }),
        ('Clinical Context', {
            'fields': ('clinical_significance', 'infection_site')
        }),
    )
