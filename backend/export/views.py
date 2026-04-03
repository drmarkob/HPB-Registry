from django.shortcuts import render, redirect
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
        
        # 2. Surgical Procedures with ALL details
        for surgery in patient.surgeries.all():
            surgery_row = {
                # Basic information
                'patient_id': patient.patient_id,
                'procedure_date': convert_to_naive(surgery.procedure_date),
                'procedure_type': surgery.get_procedure_type_display(),
                'surgical_approach': surgery.get_surgical_approach_display() if surgery.surgical_approach else 'Open',
                
                # Operative details
                'operative_time_minutes': surgery.operative_time_minutes,
                'blood_loss_ml': surgery.blood_loss_ml,
                'intraoperative_transfusion': surgery.intraoperative_transfusion,
                'transfusion_units': surgery.transfusion_units,
                'intraoperative_complications': surgery.intraoperative_complications,
                'conversion_to_open': surgery.conversion_to_open,
                'conversion_reason': surgery.conversion_reason,
                
                # Pringle maneuver
                'pringle_maneuver': surgery.pringle_maneuver,
                'pringle_time_minutes': surgery.pringle_time_minutes,
                'pringle_cycles': surgery.pringle_cycles,
                
                # Surgical Team
                'primary_surgeon': surgery.primary_surgeon.get_full_name() if surgery.primary_surgeon else None,
                'assistant_surgeon_1': surgery.assistant_surgeon_1.get_full_name() if surgery.assistant_surgeon_1 else None,
                'assistant_surgeon_2': surgery.assistant_surgeon_2.get_full_name() if surgery.assistant_surgeon_2 else None,
                'supervising_surgeon': surgery.supervising_surgeon.get_full_name() if surgery.supervising_surgeon else None,
                'anesthesiologist': surgery.anesthesiologist.get_full_name() if surgery.anesthesiologist else None,
                
                # Indication & Urgency
                'urgency': surgery.urgency,
                'indication': surgery.indication,
                'indication_other': surgery.indication_other,
                
                # Neoadjuvant Therapy
                'neoadjuvant_chemotherapy': surgery.neoadjuvant_chemotherapy,
                'neoadjuvant_radiotherapy': surgery.neoadjuvant_radiotherapy,
                'neoadjuvant_chemoradiation': surgery.neoadjuvant_chemoradiation,
                'neoadjuvant_protocol': surgery.neoadjuvant_protocol,
                'days_from_neoadjuvant_to_surgery': surgery.days_from_neoadjuvant_to_surgery,
                
                # Postoperative outcomes
                'clavien_dindo_grade': surgery.clavien_dindo_grade,
                'hospital_stay_days': surgery.hospital_stay_days,
                'icu_stay_days': surgery.icu_stay_days,
                'enhanced_recovery_protocol': surgery.enhanced_recovery_protocol,
                
                # Readmission
                'readmission_30d': surgery.readmission_30d,
                'readmission_90d': surgery.readmission_90d,
                'readmission_reason': surgery.readmission_reason,
                
                # Mortality
                'mortality_30d': surgery.mortality_30d,
                'mortality_90d': surgery.mortality_90d,
                'mortality_in_hospital': surgery.mortality_in_hospital,
                'date_of_death_if_known': convert_to_naive(surgery.date_of_death_if_known),
                
                # Quality metrics
                'operative_report_available': surgery.operative_report_available,
                'operative_report_link': surgery.operative_report_link,
            }
            
            # Add Liver Resection Details if they exist
            if hasattr(surgery, 'liver_details') and surgery.liver_details:
                liver = surgery.liver_details
                surgery_row.update({
                    'liver_resection_type': liver.get_resection_type_display(),
                    'liver_hepatectomy_type': liver.get_hepatectomy_type_display(),
                    'liver_number_of_segments': liver.number_of_segments,
                    'liver_total_tumor_count': liver.total_tumor_count,
                    'liver_largest_tumor_size_cm': liver.largest_tumor_size_cm,
                    'liver_margin_status': liver.margin_status,
                    'liver_margin_distance_mm': liver.margin_distance_mm,
                    'liver_parenchyma_quality': liver.get_parenchyma_quality_display(),
                    'liver_flr_percentage': liver.flr_percentage,
                    'liver_seg1': liver.segment_1,
                    'liver_seg2': liver.segment_2,
                    'liver_seg3': liver.segment_3,
                    'liver_seg4a': liver.segment_4a,
                    'liver_seg4b': liver.segment_4b,
                    'liver_seg5': liver.segment_5,
                    'liver_seg6': liver.segment_6,
                    'liver_seg7': liver.segment_7,
                    'liver_seg8': liver.segment_8,
                })
            
            # Add Pancreatic Resection Details if they exist
            if hasattr(surgery, 'pancreatic_details') and surgery.pancreatic_details:
                pancreas = surgery.pancreatic_details
                surgery_row.update({
                    'pancreas_variant': pancreas.get_pancreatectomy_variant_display(),
                    'pancreas_tumor_location': pancreas.get_tumor_location_display(),
                    'pancreas_tumor_size_cm': pancreas.tumor_size_cm,
                    'pancreas_duct_dilated': pancreas.pancreatic_duct_dilated,
                    'pancreas_duct_size_mm': pancreas.pancreatic_duct_size_mm,
                    'pancreas_texture': pancreas.get_pancreatic_texture_display(),
                    'pancreas_anastomosis_type': pancreas.get_anastomosis_type_display(),
                    'pancreas_drain_amylase_pod1': pancreas.drain_amylase_pod1,
                    'pancreas_drain_amylase_pod3': pancreas.drain_amylase_pod3,
                    'pancreas_portal_vein_invasion': pancreas.portal_vein_invasion,
                    'pancreas_portal_vein_resection': pancreas.portal_vein_resection,
                    'pancreas_smv_invasion': pancreas.superior_mesenteric_vein_invasion,
                    'pancreas_sma_invasion': pancreas.superior_mesenteric_artery_invasion,
                })
            
            # Add Biliary Procedure Details if they exist
            if hasattr(surgery, 'biliary_details') and surgery.biliary_details:
                biliary = surgery.biliary_details
                surgery_row.update({
                    'biliary_procedure': biliary.get_biliary_procedure_display(),
                    'biliary_bismuth_class': biliary.get_bismuth_classification_display(),
                    'biliary_duct_diameter_mm': biliary.bile_duct_diameter_mm,
                    'biliary_duct_stricture': biliary.bile_duct_stricture,
                    'biliary_anastomosis_level': biliary.get_anastomosis_level_display(),
                    'biliary_number_anastomoses': biliary.number_of_anastomoses,
                    'biliary_preop_stent': biliary.preoperative_stent,
                    'biliary_postop_stent': biliary.postoperative_stent,
                    'biliary_ercp': biliary.ercp_performed,
                    'biliary_ptbd': biliary.ptbd_performed,
                })
            
            # Add POPF details if they exist
            if hasattr(surgery, 'popf_detail') and surgery.popf_detail:
                popf = surgery.popf_detail
                surgery_row.update({
                    'popf_grade': popf.grade,
                    'popf_drain_amylase_pod3': popf.drain_amylase_pod3,
                    'popf_drain_amylase_ratio': popf.drain_amylase_ratio,
                    'popf_antibiotics': popf.antibiotics_required,
                    'popf_interventional_radiology': popf.interventional_radiology,
                    'popf_reoperation': popf.reoperation_required,
                    'popf_icu_admission': popf.icu_admission,
                    'popf_death_attributed': popf.death_attributed,
                    'popf_resolved_days': popf.resolved_days,
                })

            # Add PHLF details if they exist
            if hasattr(surgery, 'phlf_detail') and surgery.phlf_detail:
                phlf = surgery.phlf_detail
                surgery_row.update({
                    'phlf_grade': phlf.grade,
                    'phlf_bilirubin_pod5': phlf.bilirubin_pod5,
                    'phlf_inr_pod5': phlf.inr_pod5,
                    'phlf_ascites': phlf.ascites_requiring_diuretics,
                    'phlf_encephalopathy': phlf.encephalopathy_present,
                    'phlf_coagulopathy': phlf.coagulopathy_requiring_ffp,
                    'phlf_renal_failure': phlf.renal_failure,
                    'phlf_respiratory_failure': phlf.respiratory_failure,
                    'phlf_reoperation': phlf.reoperation_required,
                    'phlf_death_attributed': phlf.death_attributed,
                })

            # Add sarcopenia assessment if exists
            if hasattr(surgery, 'sarcopenia_assessments') and surgery.sarcopenia_assessments.exists():
                sarc = surgery.sarcopenia_assessments.first()
                surgery_row.update({
                    'sarcopenia_smi': sarc.skeletal_muscle_index_cm2_m2,
                    'sarcopenia_psoas': sarc.psoas_muscle_area_cm2,
                    'is_sarcopenic': sarc.is_sarcopenic,
                    'sarcopenia_ct_date': convert_to_naive(sarc.ct_date),
                })
            
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

@staff_member_required
def import_patients(request):
    """Import patients from Excel/CSV file"""
    from django.contrib import messages
    import pandas as pd
    from patients.models import Patient
    from medical_codes.models import Diagnosis
    
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        
        try:
            if excel_file.name.endswith('.csv'):
                df = pd.read_csv(excel_file)
            else:
                df = pd.read_excel(excel_file)
            
            imported = 0
            errors = []
            
            for idx, row in df.iterrows():
                try:
                    dob = None
                    if pd.notna(row.get('date_of_birth')):
                        try:
                            dob = pd.to_datetime(row['date_of_birth']).date()
                        except:
                            pass
                    
                    diagnosis = None
                    diag_code = row.get('diagnosis_icd10')
                    if diag_code and pd.notna(diag_code):
                        try:
                            diagnosis = Diagnosis.objects.get(icd10_code=diag_code)
                        except Diagnosis.DoesNotExist:
                            pass
                    
                    patient_data = {
                        'patient_id': str(row.get('patient_id', '')).strip(),
                        'first_name': str(row.get('first_name', '')).strip(),
                        'last_name': str(row.get('last_name', '')).strip(),
                        'date_of_birth': dob,
                        'gender': row.get('gender', 'M') if pd.notna(row.get('gender')) else 'M',
                        'email': str(row.get('email', '')) if pd.notna(row.get('email')) else '',
                        'phone': str(row.get('phone', '')) if pd.notna(row.get('phone')) else '',
                        'smoking_status': row.get('smoking_status', '') if pd.notna(row.get('smoking_status')) else '',
                        'diabetes': bool(row.get('diabetes', False)) if pd.notna(row.get('diabetes')) else False,
                        'hypertension': bool(row.get('hypertension', False)) if pd.notna(row.get('hypertension')) else False,
                        'height': float(row['height_cm']) if pd.notna(row.get('height_cm')) else None,
                        'weight': float(row['weight_kg']) if pd.notna(row.get('weight_kg')) else None,
                        'main_diagnosis': diagnosis,
                    }
                    
                    if patient_data['patient_id'] and patient_data['first_name'] and patient_data['last_name']:
                        # Set current user for audit
                        from hpb_registry.middleware.audit import _thread_locals
                        _thread_locals.user = request.user
                        
                        patient, created = Patient.objects.update_or_create(
                            patient_id=patient_data['patient_id'],
                            defaults=patient_data
                        )
                        imported += 1
                
                except Exception as e:
                    errors.append(f"Row {idx+2}: {str(e)}")
            
            messages.success(request, f'Successfully imported {imported} patients')
            if errors:
                messages.warning(request, f'Errors encountered: {len(errors)}')
        
        except Exception as e:
            messages.error(request, f'Import failed: {str(e)}')
        
        return redirect('export_dashboard')
    
    return render(request, 'export/import.html')
