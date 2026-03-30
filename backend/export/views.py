from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime
import pandas as pd

from patients.models import Patient
from scoring.models import MELDScore, ASAScore, ChildPughScore, CharlsonComorbidity
from clinical.models import SurgicalProcedure, ChemotherapyProtocol, FollowUp
from pathology.models import PathologyReport
from laboratory.models import LaboratoryPanel, TumorMarkerPanel

def convert_to_naive(dt):
    """Convert timezone-aware datetime to naive datetime for Excel compatibility"""
    if dt is None:
        return None
    if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

@staff_member_required
def export_dashboard(request):
    """Dashboard for export options - shows HTML page with export buttons"""
    context = {
        'patient_count': Patient.objects.count(),
        'surgery_count': SurgicalProcedure.objects.count(),
        'pathology_count': PathologyReport.objects.count(),
        'lab_count': LaboratoryPanel.objects.count(),
        'last_export': request.session.get('last_export', None),
    }
    return render(request, 'export/dashboard.html', context)

@staff_member_required
def export_complete_data(request):
    """Export complete dataset to Excel"""
    
    print("Starting data export...")
    
    # Initialize data containers
    patients_data = []
    surgery_data = []
    pathology_data = []
    labs_data = []
    tumor_markers_data = []
    followup_data = []
    
    # Get all patients
    patients = Patient.objects.all()
    
    for patient in patients:
        print(f"Processing patient: {patient.patient_id}")
        
        # 1. Patient Demographics
        patient_row = {
            'patient_id': patient.patient_id,
            'jmbg': patient.jmbg,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'age': patient.age,
            'gender': patient.gender,
            'date_of_birth': convert_to_naive(patient.date_of_birth),
            'main_diagnosis': patient.main_diagnosis.diagnosis_name if patient.main_diagnosis else None,
            'main_diagnosis_code': patient.main_diagnosis.icd10_code if patient.main_diagnosis else None,
            'smoking_status': patient.smoking_status,
            'diabetes': patient.diabetes,
            'hypertension': patient.hypertension,
            'bmi': patient.bmi,
            'created_at': convert_to_naive(patient.created_at),
        }
        patients_data.append(patient_row)
        
        # 2. Surgical Procedures
        for surgery in patient.surgeries.all():
            surgery_row = {
                'patient_id': patient.patient_id,
                'procedure_date': convert_to_naive(surgery.procedure_date),
                'procedure_type': surgery.get_procedure_type_display(),
                'surgical_approach': surgery.get_surgical_approach_display() if surgery.surgical_approach else 'Open',
                'operative_time_minutes': surgery.operative_time_minutes,
                'blood_loss_ml': surgery.blood_loss_ml,
                'popf_present': surgery.popf_present,
                'clavien_dindo_grade': surgery.clavien_dindo_grade,
                'bile_leak': surgery.bile_leak,
                'hospital_stay_days': surgery.hospital_stay_days,
                'readmission_30d': surgery.readmission_30d,
            }
            surgery_data.append(surgery_row)
        
        # 3. Pathology Reports
        for path in patient.pathology_reports.all():
            path_row = {
                'patient_id': patient.patient_id,
                'report_date': convert_to_naive(path.report_date),
                'specimen_type': path.get_specimen_type_display(),
                'diagnosis': path.diagnosis.diagnosis_name if path.diagnosis else None,
                'diagnosis_code': path.diagnosis.icd10_code if path.diagnosis else None,
                'histological_type': path.histological_type.name if path.histological_type else path.histological_type_other,
                'tumor_size_cm': path.tumor_size_cm,
                'margin_status': path.margin_status,
                'lymph_nodes_positive': path.lymph_nodes_positive,
                'lymph_nodes_examined': path.lymph_nodes_examined,
                't_stage': path.t_stage,
                'n_stage': path.n_stage,
                'm_stage': path.m_stage,
            }
            pathology_data.append(path_row)
        
        # 4. Laboratory Panels
        for lab in patient.laboratory_panels.all():
            lab_row = {
                'patient_id': patient.patient_id,
                'collection_date': convert_to_naive(lab.collection_date),
                'timing': lab.get_timing_display(),
                'hemoglobin': lab.hemoglobin,
                'wbc': lab.wbc,
                'platelets': lab.platelets,
                'alt': lab.alt,
                'ast': lab.ast,
                'total_bilirubin': lab.total_bilirubin,
                'albumin': lab.albumin,
                'inr': lab.inr,
                'creatinine': lab.creatinine,
                'crp': lab.crp,
            }
            labs_data.append(lab_row)
        
        # 5. Tumor Markers
        for marker in patient.tumor_markers.all():
            marker_row = {
                'patient_id': patient.patient_id,
                'collection_date': convert_to_naive(marker.collection_date),
                'timing': marker.get_timing_display(),
                'ca19_9': marker.ca19_9,
                'cea': marker.cea,
                'afp': marker.afp,
                'chromogranin_a': marker.chromogranin_a,
            }
            tumor_markers_data.append(marker_row)
        
        # 6. Follow-up
        for fu in patient.followups.all():
            fu_row = {
                'patient_id': patient.patient_id,
                'followup_date': convert_to_naive(fu.followup_date),
                'alive': fu.alive,
                'date_of_death': convert_to_naive(fu.date_of_death),
                'recurrence': fu.recurrence,
                'recurrence_date': convert_to_naive(fu.recurrence_date),
                'ecog_status': fu.ecog_status,
                'survival_months': fu.survival_months,
            }
            followup_data.append(fu_row)
    
    # Create Excel file
    print("Creating Excel file...")
    output = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    output['Content-Disposition'] = f'attachment; filename="HPB_Registry_Export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if patients_data:
            pd.DataFrame(patients_data).to_excel(writer, sheet_name='Patients', index=False)
        if surgery_data:
            pd.DataFrame(surgery_data).to_excel(writer, sheet_name='Surgical_Procedures', index=False)
        if pathology_data:
            pd.DataFrame(pathology_data).to_excel(writer, sheet_name='Pathology', index=False)
        if labs_data:
            pd.DataFrame(labs_data).to_excel(writer, sheet_name='Laboratory', index=False)
        if tumor_markers_data:
            pd.DataFrame(tumor_markers_data).to_excel(writer, sheet_name='Tumor_Markers', index=False)
        if followup_data:
            pd.DataFrame(followup_data).to_excel(writer, sheet_name='Follow_Up', index=False)
        
        # Metadata
        metadata = pd.DataFrame({
            'Export_Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            'Total_Patients': [len(patients_data)],
            'Data_Source': ['HPB Surgery Registry'],
        })
        metadata.to_excel(writer, sheet_name='Metadata', index=False)
    
    print(f"Export complete!")
    return output

@staff_member_required
def export_summary_stats(request):
    """Export summary statistics to Excel"""
    
    stats_data = {
        'Total Patients': Patient.objects.count(),
        'Total Surgeries': SurgicalProcedure.objects.count(),
        'Pathology Reports': PathologyReport.objects.count(),
        'Laboratory Tests': LaboratoryPanel.objects.count(),
        'Tumor Marker Tests': TumorMarkerPanel.objects.count(),
        'Follow-ups': FollowUp.objects.count(),
    }
    
    df = pd.DataFrame(list(stats_data.items()), columns=['Metric', 'Value'])
    
    output = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    output['Content-Disposition'] = f'attachment; filename="HPB_Registry_Summary_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Summary_Stats', index=False)
    
    return output

@staff_member_required
def export_patient_data(request, patient_id):
    """Export data for a single patient"""
    try:
        patient = Patient.objects.get(patient_id=patient_id)
        return HttpResponse(f"Export for patient {patient_id} - Coming soon!")
    except Patient.DoesNotExist:
        return HttpResponse("Patient not found", status=404)
