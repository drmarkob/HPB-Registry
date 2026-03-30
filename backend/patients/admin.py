from django.contrib import admin
from django.contrib.auth.models import User
from .models import Patient
from hpb_registry.middleware.audit import get_current_user

class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'full_name', 'age', 'gender', 'status', 'created_at', 'created_by']
    list_filter = ['status', 'gender']
    search_fields = ['patient_id', 'first_name', 'last_name', 'mrn', 'jmbg']
    
    # Hide audit fields - auto-populated
    exclude = ['created_by', 'updated_by']
    
    # Organize fields into sections
    fieldsets = (
        ('Basic Information', {
            'fields': ('patient_id', 'mrn', 'jmbg', 'first_name', 'last_name', 'date_of_birth', 'gender', 'status')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address', 'city', 'country'),
            'classes': ('collapse',)
        }),
        ('Anthropometric Data', {
            'fields': ('height', 'weight'),
            'classes': ('collapse',)
        }),
        ('Clinical Information', {
            'fields': ('main_diagnosis', 'smoking_status', 'clinical_notes'),
            'classes': ('collapse',)
        }),
        ('Comorbidities', {
            'fields': ('diabetes', 'hypertension', 'copd', 'coronary_artery_disease', 'chronic_kidney_disease'),
            'classes': ('collapse',)
        }),
        ('Follow-up Information', {
            'fields': ('date_of_death',),  # Removed last_followup_date
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        """Auto-populate created_by and updated_by"""
        current_user = request.user
        
        if not obj.pk:  # New object
            obj.created_by = current_user
        obj.updated_by = current_user
        
        super().save_model(request, obj, form, change)
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'
    
    def age(self, obj):
        return obj.age if obj.age else '-'
    age.short_description = 'Age'
