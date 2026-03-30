from django.urls import path
from export import views as export_views
from . import views
from .admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', views.custom_dashboard, name='dashboard'),
    path('export/dashboard/', export_views.export_dashboard, name='export_dashboard'),
    path('export/complete/', export_views.export_complete_data, name='export_complete'),
    path('export/summary/', export_views.export_summary_stats, name='export_summary'),
    path('export/patient/<str:patient_id>/', export_views.export_patient_data, name='export_patient'),
]
