from django.db import models
from django.contrib.auth.models import User
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
    
    user = models.OneToOneField(
        User, 
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
    
    # Account status
    is_active = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
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
    
    def has_permission(self, permission_type):
        """Check if user has specific permission"""
        role_permissions = {
            'admin': ['view', 'add', 'change', 'delete', 'export', 'manage_users'],
            'surgeon': ['view', 'add', 'change', 'export'],
            'resident': ['view', 'add', 'change'],
            'researcher': ['view', 'export'],
            'data_entry': ['view', 'add', 'change'],
            'viewer': ['view'],
        }
        return permission_type in role_permissions.get(self.role, [])
