from django.contrib import admin
from .models import GeneralComplication, PancreaticComplication, LiverComplication, POPFDetail, PostHepatectomyLiverFailure


# ============================================================================
# Inline Classes for Detailed Complications
# ============================================================================

class POPFInline(admin.StackedInline):
    """POPF details shown as inline within PancreaticComplication"""
    model = POPFDetail
    can_delete = False
    verbose_name_plural = "POPF Details (ISGPS - International Study Group for Pancreatic Surgery)"
    
    fieldsets = (
        ('ISGPS Grade', {
            'fields': ('grade',),
            'description': 'Grade A: Biochemical leak only, Grade B: Clinically relevant, Grade C: Severe requiring reoperation'
        }),
        ('Diagnostic Criteria', {
            'fields': ('drain_amylase_pod3', 'drain_amylase_ratio'),
            'classes': ('collapse',)
        }),
        ('Clinical Impact (Grade B)', {
            'fields': ('drain_retained', 'antibiotics_required', 'interventional_radiology', 'tpn_required'),
            'classes': ('collapse',)
        }),
        ('Severe Complications (Grade C)', {
            'fields': ('reoperation_required', 'icu_admission', 'death_attributed'),
            'classes': ('collapse',)
        }),
        ('Outcome', {
            'fields': ('resolved_days', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    extra = 0


class PHLFFInline(admin.StackedInline):
    """Post-hepatectomy Liver Failure details shown as inline within LiverComplication"""
    model = PostHepatectomyLiverFailure
    can_delete = False
    verbose_name_plural = "Post-hepatectomy Liver Failure Details (ISGLS - International Study Group for Liver Surgery)"
    
    fieldsets = (
        ('ISGLS Grade', {
            'fields': ('grade',),
            'description': 'Grade A: Abnormal labs only, Grade B: Non-invasive treatment, Grade C: Invasive treatment required'
        }),
        ('Diagnostic Criteria (POD 5)', {
            'fields': ('bilirubin_pod5', 'inr_pod5'),
            'classes': ('collapse',)
        }),
        ('Clinical Features', {
            'fields': ('ascites_requiring_diuretics', 'encephalopathy_present', 
                      'coagulopathy_requiring_ffp', 'renal_failure', 'respiratory_failure'),
            'classes': ('collapse',)
        }),
        ('Invasive Treatments', {
            'fields': ('reoperation_required', 'liver_transplant_required'),
            'classes': ('collapse',)
        }),
        ('Outcome', {
            'fields': ('resolved', 'resolved_days', 'death_attributed', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    extra = 0


# ============================================================================
# Admin Classes for Complications
# ============================================================================

class GeneralComplicationAdmin(admin.ModelAdmin):
    list_display = ['surgical_procedure', 'complication_type', 'onset_days', 'clavien_grade', 'resolved']
    list_filter = ['complication_type', 'clavien_grade', 'resolved']
    search_fields = ['surgical_procedure__patient__patient_id', 'surgical_procedure__patient__last_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('surgical_procedure', 'complication_type', 'onset_days', 'clavien_grade')
        }),
        ('Management', {
            'fields': ('treatment', 'resolved', 'resolved_days')
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
    
    # POPF details shown as inline
    inlines = [POPFInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('surgical_procedure', 'complication_type', 'onset_days', 'clavien_grade')
        }),
        ('Management', {
            'fields': ('treatment', 'resolved', 'resolved_days')
        }),
        ('Pancreatic Specific', {
            'fields': ('drain_amylase_pod1', 'drain_amylase_pod3', 'drain_output_ml'),
            'classes': ('collapse',)
        }),
        ('Outcome', {
            'fields': ('resolved_completely', 'sequelae'),
            'classes': ('collapse',)
        }),
    )


class LiverComplicationAdmin(admin.ModelAdmin):
    list_display = ['surgical_procedure', 'complication_type', 'onset_days', 'clavien_grade', 'resolved']
    list_filter = ['complication_type', 'clavien_grade', 'resolved']
    search_fields = ['surgical_procedure__patient__patient_id', 'surgical_procedure__patient__last_name']
    
    # PHLF details shown as inline
    inlines = [PHLFFInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('surgical_procedure', 'complication_type', 'onset_days', 'clavien_grade')
        }),
        ('Management', {
            'fields': ('treatment', 'resolved', 'resolved_days')
        }),
        ('Liver Specific', {
            'fields': ('bilirubin_pod5', 'inr_pod5', 'ascites_volume_ml', 'diuretic_required'),
            'classes': ('collapse',)
        }),
        ('Outcome', {
            'fields': ('resolved_completely', 'sequelae'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# Register Models with Admin Site
# ============================================================================

admin.site.register(GeneralComplication, GeneralComplicationAdmin)
admin.site.register(PancreaticComplication, PancreaticComplicationAdmin)
admin.site.register(LiverComplication, LiverComplicationAdmin)
