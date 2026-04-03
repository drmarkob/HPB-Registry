from django.db import models
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.models import Group as AuthGroup
from django.core.exceptions import ValidationError


class UserProfile(models.Model):
    """Extended user profile for role-based access control"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator - Full system access'),
        ('surgeon', 'Surgeon - Full patient data access'),
        ('resident', 'Resident - Edit access, limited admin'),
        ('researcher', 'Researcher - Read-only for research'),
        ('data_entry', 'Data Entry - Create/edit records'),
        ('viewer', 'View Only - Read-only access'),
    ]
    
    # Data anonymization levels for researchers
    ANONYMIZATION_CHOICES = [
        ('none', 'No anonymization - full access'),
        ('partial', 'Partial - Names hidden, dates shifted by ±7 days'),
        ('full', 'Full - Complete de-identification for research'),
    ]
    
    user = models.OneToOneField(
        AuthUser, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='viewer',
        help_text="User role determines access level"
    )
    
    # Professional information
    department = models.CharField(max_length=100, blank=True)
    institution = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=100, blank=True, help_text="e.g., Dr., Prof., etc.")
    
    # Contact information
    phone = models.CharField(max_length=20, blank=True)
    institution_email = models.EmailField(blank=True, help_text="Work email")
    
    # Research interests
    research_interests = models.TextField(blank=True, help_text="Areas of research interest")
    
    # Data anonymization (for researchers)
    anonymization_level = models.CharField(
        max_length=20, 
        choices=ANONYMIZATION_CHOICES, 
        default='none',
        help_text="Level of data anonymization for research users"
    )
    
    # Account status
    is_active = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        AuthUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='profiles_created'
    )
    
    class Meta:
        ordering = ['user__username']
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_role_display()}"
    
    def clean(self):
        """Validate user profile data"""
        if self.user.is_superuser and self.role != 'admin':
            raise ValidationError({'role': 'Superusers must have admin role'})
    
    def has_permission(self, permission_type, model_name=None):
        """
        Check if user has specific permission.
        
        Args:
            permission_type: 'view', 'add', 'change', 'delete', 'export', 'manage_users'
            model_name: Optional model name for model-specific permissions
        """
        # Admin has all permissions
        if self.role == 'admin':
            return True
        
        # Define role-based permissions
        role_permissions = {
            'admin': ['view', 'add', 'change', 'delete', 'export', 'manage_users'],
            'surgeon': ['view', 'add', 'change', 'export'],
            'resident': ['view', 'add', 'change'],
            'researcher': ['view', 'export'],
            'data_entry': ['view', 'add', 'change'],
            'viewer': ['view'],
        }
        
        # Check basic permission
        if permission_type not in role_permissions.get(self.role, []):
            return False
        
        # Model-specific restrictions
        if model_name:
            # Researchers cannot view patient names (anonymization handled separately)
            if self.role == 'researcher' and model_name == 'Patient':
                return permission_type == 'view'
            
            # Data entry cannot delete
            if self.role == 'data_entry' and permission_type == 'delete':
                return False
            
            # Residents cannot delete
            if self.role == 'resident' and permission_type == 'delete':
                return False
        
        return True
    
    def get_anonymized_patient_data(self, patient):
        """
        Return anonymized patient data based on user role.
        Called by the admin when displaying patient data.
        """
        if self.role != 'researcher' or self.anonymization_level == 'none':
            return patient
        
        from datetime import timedelta
        import random
        random.seed(patient.id)  # Consistent anonymization for same patient
        
        if self.anonymization_level == 'partial':
            # Create anonymized version
            class AnonymizedPatient:
                def __init__(self, original):
                    self.id = original.id
                    self.patient_id = f"RES-{original.id:06d}"
                    self.first_name = "[REDACTED]"
                    self.last_name = "[REDACTED]"
                    self.jmbg = None
                    self.mrn = None
                    self.phone = None
                    self.email = None
                    self.address = None
                    self.city = None
                    
                    # Shift dates by -7 to +7 days
                    if original.date_of_birth:
                        shift_days = random.randint(-7, 7)
                        self.date_of_birth = original.date_of_birth + timedelta(days=shift_days)
                    else:
                        self.date_of_birth = None
                    
                    # Keep clinical data
                    self.gender = original.gender
                    self.age = original.age
                    self.main_diagnosis = original.main_diagnosis
                    self.smoking_status = original.smoking_status
                    self.diabetes = original.diabetes
                    self.hypertension = original.hypertension
                    self.bmi = original.bmi
                    self.status = original.status
            
            return AnonymizedPatient(patient)
        
        elif self.anonymization_level == 'full':
            # Complete de-identification
            class FullyAnonymizedPatient:
                def __init__(self, original):
                    self.id = original.id
                    self.patient_id = f"ANON-{original.id:06d}"
                    self.first_name = "ANONYMOUS"
                    self.last_name = "ANONYMOUS"
                    self.jmbg = None
                    self.mrn = None
                    self.phone = None
                    self.email = None
                    self.address = None
                    self.city = None
                    self.date_of_birth = None
                    self.gender = original.gender if random.random() > 0.3 else None
                    self.age = original.age if original.age and random.random() > 0.5 else None
                    self.main_diagnosis = original.main_diagnosis
                    self.smoking_status = None
                    self.diabetes = None
                    self.hypertension = None
                    self.bmi = None
                    self.status = original.status
            
            return FullyAnonymizedPatient(patient)
        
        return patient


class AuditLog(models.Model):
    """Track user actions for compliance and research integrity"""
    
    ACTION_CHOICES = [
        ('view', 'View'),
        ('add', 'Add'),
        ('change', 'Change'),
        ('delete', 'Delete'),
        ('export', 'Export'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('import', 'Import'),
        ('backup', 'Backup'),
    ]
    
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100, help_text="Model accessed (e.g., Patient, SurgicalProcedure)")
    object_id = models.CharField(max_length=100, blank=True, help_text="ID of the object")
    object_repr = models.CharField(max_length=200, blank=True, help_text="String representation")
    details = models.TextField(blank=True, help_text="Additional details about the action")
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} - {self.timestamp}"


# Proxy models to move User and Group to users app in admin
class User(AuthUser):
    """Proxy model to move User to users app in admin"""
    class Meta:
        proxy = True
        verbose_name = "User"
        verbose_name_plural = "Users"


class Group(AuthGroup):
    """Proxy model to move Group to users app in admin"""
    class Meta:
        proxy = True
        verbose_name = "Group"
        verbose_name_plural = "Groups"
