import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Generate Excel template for patient import'
    
    def handle(self, *args, **options):
        template_data = {
            'patient_id': ['PAT001', 'PAT002', 'PAT003'],
            'first_name': ['John', 'Jane', 'Robert'],
            'last_name': ['Smith', 'Doe', 'Johnson'],
            'date_of_birth': ['1970-01-15', '1985-03-22', '1990-07-10'],
            'gender': ['M', 'F', 'M'],
            'email': ['john.smith@email.com', 'jane.doe@email.com', 'robert.johnson@email.com'],
            'phone': ['+381611234567', '+381612345678', '+381613456789'],
            'smoking_status': ['never', 'former', 'current'],
            'diabetes': [False, True, False],
            'hypertension': [True, False, True],
            'diagnosis_icd10': ['C22.0', 'C25.0', 'K80.5'],
            'height_cm': [175, 162, 180],
            'weight_kg': [80, 58, 85],
        }
        
        df = pd.DataFrame(template_data)
        
        instructions = pd.DataFrame({
            'Field': [
                'patient_id', 'first_name', 'last_name', 'date_of_birth', 'gender',
                'email', 'phone', 'smoking_status', 'diabetes', 'hypertension',
                'diagnosis_icd10', 'height_cm', 'weight_kg'
            ],
            'Description': [
                'Unique patient identifier', 'First name', 'Last name', 'Date of birth (YYYY-MM-DD)',
                'Gender: M/F/O', 'Email address', 'Phone number', 'Smoking: never/former/current',
                'Diabetes (True/False)', 'Hypertension (True/False)',
                'ICD-10 code from Diagnosis table', 'Height in cm', 'Weight in kg'
            ],
            'Required': ['Yes', 'Yes', 'Yes', 'No', 'Yes', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No'],
            'Example': ['PAT001', 'John', 'Smith', '1970-01-15', 'M', 'john@email.com', '+381611234567', 'never', 'False', 'True', 'C22.0', '175', '80']
        })
        
        # Save template
        template_dir = os.path.join(settings.BASE_DIR, '..', 'import_templates')
        os.makedirs(template_dir, exist_ok=True)
        template_path = os.path.join(template_dir, 'patient_import_template.xlsx')
        
        with pd.ExcelWriter(template_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Patient Data', index=False)
            instructions.to_excel(writer, sheet_name='Instructions', index=False)
        
        self.stdout.write(self.style.SUCCESS(f"Template created: {template_path}"))
