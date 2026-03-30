from django.db import models
from .middleware.audit import get_current_user

class AuditMixin(models.Model):
    """Mixin to automatically populate audit fields"""
    
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """Auto-populate created_by and updated_by"""
        current_user = get_current_user()
        
        if not self.pk:  # New object being created
            if current_user and not self.created_by:
                self.created_by = current_user
        else:  # Existing object being updated
            if current_user and not self.updated_by:
                self.updated_by = current_user
        
        super().save(*args, **kwargs)
