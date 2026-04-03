from .admin import admin_site
from django.urls import path
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from export import views as export_views
from . import views


# Helper function to check if user is admin
def is_admin(user):
    """Check if user has admin role or is superuser"""
    return user.is_authenticated and (
        user.is_superuser or 
        (hasattr(user, 'profile') and user.profile.role == 'admin')
    )


# Role management view (only accessible to admin users)
@user_passes_test(is_admin)
def role_management(request):
    """View for user role management and permissions reference"""
    return render(request, 'admin/users/role_management.html')


urlpatterns = [
    # Admin
    path('admin/', admin_site.urls),
    path('admin/role-management/', role_management, name='role_management'),
    
    # Dashboard
    path('', views.custom_dashboard, name='dashboard'),
    
    # Export
    path('export/dashboard/', export_views.export_dashboard, name='export_dashboard'),
    path('export/complete/', export_views.export_complete_data, name='export_complete'),
    path('export/summary/', export_views.export_summary_stats, name='export_summary'),
    path('export/patient/<str:patient_id>/', export_views.export_patient_data, name='export_patient'),
    path('export/import/', export_views.import_patients, name='import_patients'),
]
