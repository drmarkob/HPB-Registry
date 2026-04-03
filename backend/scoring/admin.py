from django.contrib import admin
from scoring.models import SarcopeniaAssessment
from .models import (MELDScore, ASAScore, ChildPughScore, CharlsonComorbidity,
                     FibrosisScore, NutritionalRiskIndex)


class MELDScoreAdmin(admin.ModelAdmin):
    list_display = ['patient', 'date_assessed', 'score', 'meld_na']
    list_filter = ['date_assessed']
    search_fields = ['patient__patient_id', 'patient__last_name']
    readonly_fields = ['score', 'meld_na']


class ASAScoreAdmin(admin.ModelAdmin):
    list_display = ['patient', 'date_assessed', 'asa_class', 'emergency']
    list_filter = ['asa_class', 'emergency', 'date_assessed']
    search_fields = ['patient__patient_id', 'patient__last_name']


class ChildPughScoreAdmin(admin.ModelAdmin):
    list_display = ['patient', 'date_assessed', 'score', 'class_grade']
    list_filter = ['date_assessed']
    search_fields = ['patient__patient_id', 'patient__last_name']
    readonly_fields = ['score', 'class_grade']


class CharlsonComorbidityAdmin(admin.ModelAdmin):
    list_display = ['patient', 'date_assessed', 'score']
    list_filter = ['date_assessed']
    search_fields = ['patient__patient_id', 'patient__last_name']
    readonly_fields = ['score']


class FibrosisScoreAdmin(admin.ModelAdmin):
    list_display = ['patient', 'date_assessed', 'fib4_score', 'fib4_category', 'apri_score', 'apri_category']
    list_filter = ['fib4_category', 'apri_category', 'date_assessed']
    search_fields = ['patient__patient_id', 'patient__last_name']
    readonly_fields = ['fib4_score', 'fib4_category', 'apri_score', 'apri_category']


class NutritionalRiskIndexAdmin(admin.ModelAdmin):
    list_display = ['patient', 'date_assessed', 'nri_score', 'category']
    list_filter = ['category', 'date_assessed']
    search_fields = ['patient__patient_id', 'patient__last_name']
    readonly_fields = ['nri_score', 'category']


class SarcopeniaAssessmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'date_assessed', 'skeletal_muscle_index_cm2_m2', 'is_sarcopenic']
    list_filter = ['is_sarcopenic', 'date_assessed']
    search_fields = ['patient__patient_id', 'patient__last_name']
    readonly_fields = ['is_sarcopenic', 'date_assessed']  # Add 'date_assessed' here
    
    fieldsets = (
        ('Patient', {'fields': ('patient',)}),
        ('Assessment Date', {'fields': ('date_assessed',)}),  # Add this section
        ('CT Measurements', {'fields': ('skeletal_muscle_index_cm2_m2', 'psoas_muscle_area_cm2',
                                        'visceral_fat_area_cm2', 'subcutaneous_fat_area_cm2')}),
        ('Patient Information', {'fields': ('gender', 'ct_date', 'ct_slice_location')}),
        ('Sarcopenia Status', {'fields': ('is_sarcopenic',)}),
        ('Notes', {'fields': ('notes',)}),
    )


# Register all models
admin.site.register(MELDScore, MELDScoreAdmin)
admin.site.register(ASAScore, ASAScoreAdmin)
admin.site.register(ChildPughScore, ChildPughScoreAdmin)
admin.site.register(CharlsonComorbidity, CharlsonComorbidityAdmin)
admin.site.register(FibrosisScore, FibrosisScoreAdmin)
admin.site.register(NutritionalRiskIndex, NutritionalRiskIndexAdmin)
admin.site.register(SarcopeniaAssessment, SarcopeniaAssessmentAdmin)
