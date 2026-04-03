import pandas as pd
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db import transaction
from patients.models import Patient
from medical_codes.models import Diagnosis
from django.contrib.auth.models import User
from hpb_registry.middleware.audit import _thread_locals

class Command(BaseCommand):
    help = 'Import patients from Excel/CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to Excel/CSV file')
        parser.add_argument('--dry-run', action='store_true', help='Validate without importing')
        parser.add_argument('--skip-errors', action='store_true', help='Skip problematic rows')
        parser.add_argument('--user', type=str, help='Username to set as created_by (default: first superuser)')
    
    def handle(self, *args, **options):
        file_path = options['file_path']
        dry_run = options['dry_run']
        skip_errors = options['skip_errors']
        username = options.get('user')
        
        # Set a default user for audit
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
                return
        else:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                self.stdout.write(self.style.WARNING('No superuser found, will set created_by = None'))
        
        # Temporarily set the user in thread locals so AuditMixin can use it
        if user:
            _thread_locals.user = user
        
        # Read file
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading file: {e}'))
            return
        
        self.stdout.write(f"Found {len(df)} rows to process")
        
        imported = 0
        errors = []
        
        # Use a savepoint for dry-run (will be rolled back)
        savepoint = None
        
        try:
            if dry_run:
                savepoint = transaction.savepoint()
            
            for idx, row in df.iterrows():
                try:
                    # Parse date of birth
                    dob = None
                    if pd.notna(row.get('date_of_birth')):
                        try:
                            dob = pd.to_datetime(row['date_of_birth']).date()
                        except:
                            pass
                    
                    # Look up diagnosis
                    diagnosis = None
                    diag_code = row.get('diagnosis_icd10')
                    if diag_code and pd.notna(diag_code):
                        try:
                            diagnosis = Diagnosis.objects.get(icd10_code=diag_code)
                        except Diagnosis.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f"Row {idx+2}: Diagnosis {diag_code} not found"))
                    
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
                    
                    # Validate required fields
                    if not patient_data['patient_id']:
                        raise ValueError("patient_id is required")
                    if not patient_data['first_name']:
                        raise ValueError("first_name is required")
                    if not patient_data['last_name']:
                        raise ValueError("last_name is required")
                    
                    # Create or update patient
                    patient, created = Patient.objects.update_or_create(
                        patient_id=patient_data['patient_id'],
                        defaults=patient_data
                    )
                    
                    imported += 1
                    if created:
                        self.stdout.write(f"✓ Created: {patient.patient_id} - {patient.full_name}")
                    else:
                        self.stdout.write(f"✓ Updated: {patient.patient_id} - {patient.full_name}")
                
                except ValidationError as e:
                    error_msg = f"Row {idx+2}: Validation error - {e}"
                    self.stdout.write(self.style.ERROR(error_msg))
                    errors.append(error_msg)
                    if not skip_errors:
                        # Rollback and exit
                        if dry_run and savepoint is not None:
                            transaction.savepoint_rollback(savepoint)
                        raise SystemExit(1)
                
                except Exception as e:
                    error_msg = f"Row {idx+2}: Error - {str(e)}"
                    self.stdout.write(self.style.ERROR(error_msg))
                    errors.append(error_msg)
                    if not skip_errors:
                        # Rollback and exit
                        if dry_run and savepoint is not None:
                            transaction.savepoint_rollback(savepoint)
                        raise SystemExit(1)
            
            if dry_run:
                self.stdout.write(self.style.WARNING(f"DRY RUN: Would import {imported} records"))
                if savepoint is not None:
                    transaction.savepoint_rollback(savepoint)
            else:
                self.stdout.write(self.style.SUCCESS(f"Successfully imported {imported} patients"))
            
            if errors:
                self.stdout.write(f"Errors encountered: {len(errors)}")
        
        except SystemExit:
            raise
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Unexpected error: {e}"))
            if savepoint is not None:
                transaction.savepoint_rollback(savepoint)
            raise
