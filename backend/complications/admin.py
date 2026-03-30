from django.contrib import admin
from .models import GeneralComplication, PancreaticComplication, LiverComplication

class GeneralComplicationAdmin(admin.ModelAdmin):
    list_display = ['surgical_procedure', 'complication_type', 'onset_days', 'clavien_grade', 'resolved']
    list_filter = ['complication_type', 'clavien_grade', 'resolved']
    search_fields = ['surgical_procedure__patient__patient_id', 'surgical_procedure__patient__last_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('surgical_procedure', 'complication_type', 'onset_days', 'clavien_grade')
        }),
        ('Management', {
            'fields': ('treatment', 'resolved')
        }),
        ('Details', {
            'fields': ('details',),
            'classes': ('collapse',)
        }),
    )

class PancreaticComplicationAdmin(admin.ModelAdmin):
    list_display = ['surgical_procedure', 'complication_type', 'onset_days', 'clavien_grade', 'resolved']
    list_filter = ['complication_type', 'clavien_grade', 'resolved']
    search_fields = ['surgical_procedure__patient__patient_id', 'surgical_procedure__patient__last_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('surgical_procedure', 'complication_type', 'onset_days', 'clavien_grade')
        }),
        ('Management', {
            'fields': ('treatment', 'resolved')
        }),
        ('Pancreatic Specific', {
            'fields': ('drain_amylase_pod1', 'drain_amylase_pod3'),
            'classes': ('collapse',)
        }),
    )

class LiverComplicationAdmin(admin.ModelAdmin):
    list_display = ['surgical_procedure', 'complication_type', 'onset_days', 'clavien_grade', 'resolved']
    list_filter = ['complication_type', 'clavien_grade', 'resolved']
    search_fields = ['surgical_procedure__patient__patient_id', 'surgical_procedure__patient__last_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('surgical_procedure', 'complication_type', 'onset_days', 'clavien_grade')
        }),
        ('Management', {
            'fields': ('treatment', 'resolved')
        }),
        ('Liver Specific', {
            'fields': ('bilirubin_pod5', 'inr_pod5'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(GeneralComplication, GeneralComplicationAdmin)
admin.site.register(PancreaticComplication, PancreaticComplicationAdmin)
admin.site.register(LiverComplication, LiverComplicationAdmin)
