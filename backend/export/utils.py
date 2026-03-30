import pandas as pd
from django.http import HttpResponse
from patients.models import Patient
from clinical.models import SurgicalProcedure, ChemotherapyProtocol, FollowUp
from scoring.models import MELDScore, ASAScore, ChildPughScore, CharlsonComorbidity

def export_to_excel(request):
    """Export all patient data to Excel for SPSS import"""
    
    # Collect all data
    patients = Patient.objects.all()
    
    # Create main dataframe
    data = []
    for patient in patients:
        # Get latest scores
        meld = MELDScore.objects.filter(patient=patient).first()
        asa = ASAScore.objects.filter(patient=patient).first()
        child_pugh = ChildPughScore.objects.filter(patient=patient).first()
        charlson = CharlsonComorbidity.objects.filter(patient=patient).first()
        
        # Get latest surgery
        surgery = SurgicalProcedure.objects.filter(patient=patient).first()
        
        row = {
            'patient_id': patient.patient_id,
            'age': patient.age,
            'gender': patient.gender,
            'smoking': patient.smoking_status,
            'diabetes': patient.diabetes,
            'hypertension': patient.hypertension,
            'meld_score': meld.score if meld else None,
            'asa_class': asa.asa_class if asa else None,
            'child_pugh_score': child_pugh.score if child_pugh else None,
            'child_pugh_class': child_pugh.class_grade if child_pugh else None,
            'charlson_score': charlson.score if charlson else None,
            'procedure_type': surgery.procedure_type if surgery else None,
            'operative_time': surgery.operative_time_minutes if surgery else None,
            'blood_loss': surgery.blood_loss_ml if surgery else None,
            'popf_grade': surgery.popf_grade if surgery and surgery.popf_present else None,
            'clavien_dindo': surgery.clavien_dindo_grade if surgery else None,
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Create Excel file
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="hpb_registry_export.xlsx"'
    
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Patients', index=False)
    
    return response

def export_for_spss(request):
    """Export data in SPSS-compatible format (CSV)"""
    patients = Patient.objects.all()
    
    # Similar data collection as above
    data = []
    for patient in patients:
        row = {
            'PATIENT_ID': patient.patient_id,
            'AGE': patient.age,
            'GENDER': 1 if patient.gender == 'M' else 0,
            'DIABETES': 1 if patient.diabetes else 0,
            # ... add all fields
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="hpb_registry_spss.csv"'
    
    df.to_csv(response, index=False)
    return response
