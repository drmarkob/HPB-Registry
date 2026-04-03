from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, AuditLog, User, Group


class UserProfileInline(admin.StackedInline):
    """Inline form for UserProfile within User admin"""
    model = UserProfile
    fk_name = 'user'
    can_delete = False
    verbose_name_plural = "Profile"
    fieldsets = (
        ('Role & Permissions', {
            'fields': ('role', 'anonymization_level')
        }),
        ('Professional Information', {
            'fields': ('department', 'institution', 'title', 'research_interests'),
            'classes': ('collapse',)
        }),
        ('Contact', {
            'fields': ('phone', 'institution_email'),
            'classes': ('collapse',)
        }),
    )


class CustomUserAdmin(BaseUserAdmin):
    """Custom User admin with profile inline"""
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'profile__role']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    
    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else 'No Profile'
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'profile__role'


class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model"""
    list_display = ['user', 'role', 'anonymization_level', 'department', 'institution']
    list_filter = ['role', 'anonymization_level']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'department']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Role & Permissions', {
            'fields': ('role', 'anonymization_level')
        }),
        ('Professional Information', {
            'fields': ('department', 'institution', 'title', 'research_interests')
        }),
        ('Contact', {
            'fields': ('phone', 'institution_email')
        }),
    )


class AuditLogAdmin(admin.ModelAdmin):
    """Admin for Audit Logs (read-only)"""
    list_display = ['timestamp', 'user', 'action', 'model_name', 'object_id', 'ip_address']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'object_repr', 'details']
    readonly_fields = ['timestamp', 'user', 'action', 'model_name', 'object_id', 'object_repr', 'details', 'ip_address']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Audit Information', {
            'fields': ('timestamp', 'user', 'ip_address')
        }),
        ('Action Details', {
            'fields': ('action', 'model_name', 'object_id', 'object_repr')
        }),
        ('Additional Information', {
            'fields': ('details',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Register proxy models
@admin.register(User)
class UserAdminProxy(CustomUserAdmin):
    """Admin for User proxy model"""
    pass


@admin.register(Group)
class GroupAdminProxy(admin.ModelAdmin):
    """Admin for Group proxy model"""
    list_display = ['name']
    search_fields = ['name']
