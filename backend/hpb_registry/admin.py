from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group, User
from django.contrib import admin

# Import models
from patients.models import Patient
from laboratory.models import LaboratoryPanel, TumorMarkerPanel, MicrobiologyCulture
from clinical.models import (
    SurgicalProcedure, 
    ChemotherapyProtocol, 
    FollowUp, 
    LiverResectionDetail, 
    PancreaticResectionDetail, 
    BiliaryProcedureDetail,
    TextbookOutcome  # Add this
)
from pathology.models import PathologyReport, MolecularMarkers
from scoring.models import MELDScore, ASAScore, ChildPughScore, CharlsonComorbidity
from medical_codes.models import Diagnosis, HistologyType
from complications.models import GeneralComplication, PancreaticComplication, LiverComplication

# Import custom admin classes
from patients.admin import PatientAdmin
from laboratory.admin import LaboratoryPanelAdmin, TumorMarkerPanelAdmin, MicrobiologyCultureAdmin
from clinical.admin import (
    SurgicalProcedureAdmin, 
    ChemotherapyProtocolAdmin, 
    FollowUpAdmin, 
    LiverResectionDetailAdmin, 
    PancreaticResectionDetailAdmin, 
    BiliaryProcedureDetailAdmin
)
from pathology.admin import PathologyReportAdmin, MolecularMarkersAdmin
from scoring.admin import MELDScoreAdmin, ASAScoreAdmin, ChildPughScoreAdmin, CharlsonComorbidityAdmin
from medical_codes.admin import DiagnosisAdmin, HistologyTypeAdmin
from complications.admin import GeneralComplicationAdmin, PancreaticComplicationAdmin, LiverComplicationAdmin

# Create custom admin site
class HPBAdminSite(AdminSite):
    site_header = "HPB Surgery Registry"
    site_title = "HPB Registry Admin"
    index_title = "Welcome to HPB Surgery Registry"
    
    def get_app_list(self, request, app_label=None):  # Add app_label=None
        """Return apps in the specified order"""
        app_dict = self._build_app_dict(request)
        
        # Define the exact order
        order = [
            'patients',
            'laboratory',
            'clinical',
            'pathology',
            'scoring',
            'medical_codes',
            'complications',
            'export',
            'auth',
        ]
        
        # Create ordered list
        ordered_apps = []
        for app_label_name in order:
            if app_label_name in app_dict:
                ordered_apps.append(app_dict[app_label_name])
        
        # Add any remaining apps
        for app_label_name, app in app_dict.items():
            if app_label_name not in order:
                ordered_apps.append(app)
        
        return ordered_apps

# Create an instance of the custom admin site
admin_site = HPBAdminSite(name='hpb_admin')

# Register all models with their custom admin classes
admin_site.register(Patient, PatientAdmin)
admin_site.register(LaboratoryPanel, LaboratoryPanelAdmin)
admin_site.register(TumorMarkerPanel, TumorMarkerPanelAdmin)
admin_site.register(MicrobiologyCulture, MicrobiologyCultureAdmin)
admin_site.register(SurgicalProcedure, SurgicalProcedureAdmin)
admin_site.register(LiverResectionDetail, LiverResectionDetailAdmin)
admin_site.register(PancreaticResectionDetail, PancreaticResectionDetailAdmin)
admin_site.register(BiliaryProcedureDetail, BiliaryProcedureDetailAdmin)
admin_site.register(ChemotherapyProtocol, ChemotherapyProtocolAdmin)
admin_site.register(FollowUp, FollowUpAdmin)
admin_site.register(PathologyReport, PathologyReportAdmin)
admin_site.register(MolecularMarkers, MolecularMarkersAdmin)
admin_site.register(MELDScore, MELDScoreAdmin)
admin_site.register(ASAScore, ASAScoreAdmin)
admin_site.register(ChildPughScore, ChildPughScoreAdmin)
admin_site.register(CharlsonComorbidity, CharlsonComorbidityAdmin)
admin_site.register(Diagnosis, DiagnosisAdmin)
admin_site.register(HistologyType, HistologyTypeAdmin)
admin_site.register(GeneralComplication, GeneralComplicationAdmin)
admin_site.register(PancreaticComplication, PancreaticComplicationAdmin)
admin_site.register(LiverComplication, LiverComplicationAdmin)
admin_site.register(TextbookOutcome)  # Add this line
admin_site.register(Group)
admin_site.register(User)
