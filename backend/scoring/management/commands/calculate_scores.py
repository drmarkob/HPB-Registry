"""
Management command to calculate clinical scores from existing patient data.
Usage:
    python manage.py calculate_scores                    # Calculate for all patients
    python manage.py calculate_scores --patient PAT001   # Calculate for specific patient
    python manage.py calculate_scores --dry-run          # Preview without saving
    python manage.py calculate_scores --verbose          # Show detailed calculations
"""

from django.core.management.base import BaseCommand
from patients.models import Patient
from laboratory.models import LaboratoryPanel
from scoring.models import MELDScore, ChildPughScore, ASAScore, CharlsonComorbidity
import math


class Command(BaseCommand):
    help = 'Calculate MELD, Child-Pugh, and Charlson scores from existing patient data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--patient',
            type=str,
            help='Calculate scores for a specific patient by patient_id'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be calculated without saving to database'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed calculation information'
        )
    
    def handle(self, *args, **options):
        patient_id = options.get('patient')
        dry_run = options.get('dry_run')
        verbose = options.get('verbose')
        
        # Get patients to process
        if patient_id:
            patients = Patient.objects.filter(patient_id=patient_id)
            if not patients.exists():
                self.stdout.write(self.style.ERROR(f'Patient with ID "{patient_id}" not found'))
                return
        else:
            patients = Patient.objects.all()
        
        if not patients.exists():
            self.stdout.write(self.style.WARNING('No patients found in database'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\n{"=" * 70}'))
        self.stdout.write(f'Starting score calculation for {patients.count()} patient(s)')
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE: No changes will be saved'))
        self.stdout.write(f'{"=" * 70}\n')
        
        results = {
            'meld_created': 0,
            'meld_updated': 0,
            'child_created': 0,
            'child_updated': 0,
            'charlson_created': 0,
            'charlson_updated': 0,
            'patients_with_labs': 0,
            'errors': 0
        }
        
        for patient in patients:
            self.stdout.write(f'\n📋 Patient: {patient.patient_id} - {patient.full_name}')
            if patient.date_of_birth:
                self.stdout.write(f'   Age: {patient.age} years')
            
            # Get latest lab data
            latest_lab = patient.laboratory_panels.order_by('-collection_date').first()
            
            if latest_lab:
                results['patients_with_labs'] += 1
                # Calculate MELD
                self._calculate_meld(patient, latest_lab, dry_run, verbose, results)
                # Calculate Child-Pugh
                self._calculate_child_pugh(patient, latest_lab, dry_run, verbose, results)
                # Calculate fibrosis scores
                self._calculate_fibrosis_scores(patient, dry_run, verbose, results)
            else:
                self.stdout.write(f'   ⚠ No laboratory data found')
            
            # Calculate Charlson (from CharlsonComorbidity model)
            self._calculate_charlson(patient, dry_run, verbose, results)
            
            # Check ASA (requires manual entry)
            self._check_asa(patient, verbose)
        
        # Print summary
        self.stdout.write(self.style.SUCCESS(f'\n{"=" * 70}'))
        self.stdout.write('SCORE CALCULATION SUMMARY')
        self.stdout.write(f'{"=" * 70}')
        self.stdout.write(f'📊 Patients with lab data: {results["patients_with_labs"]}')
        self.stdout.write(f'✓ MELD scores: {results["meld_created"]} created, {results["meld_updated"]} updated')
        self.stdout.write(f'✓ Child-Pugh scores: {results["child_created"]} created, {results["child_updated"]} updated')
        self.stdout.write(f'✓ Charlson scores: {results["charlson_created"]} created, {results["charlson_updated"]} updated')
        if results['errors'] > 0:
            self.stdout.write(self.style.ERROR(f'✗ Errors encountered: {results["errors"]}'))
        self.stdout.write(f'{"=" * 70}\n')
        
        # Helpful notes
        self.stdout.write('📌 Notes:')
        self.stdout.write('   • MELD/Child-Pugh require: bilirubin, INR, creatinine, albumin')
        self.stdout.write('   • For MELD: bilirubin in μmol/L, creatinine in μmol/L (auto-converted)')
        self.stdout.write('   • Child-Pugh: ascites and encephalopathy need manual entry')
        self.stdout.write('   • ASA score: requires manual entry (clinical assessment)')
        self.stdout.write('   • Charlson: auto-calculated from existing CharlsonComorbidity data\n')
    
    def _calculate_meld(self, patient, latest_lab, dry_run, verbose, results):
        """
        Calculate MELD score from laboratory data.
        
        MELD Formula: 10 * (0.957 * ln(Creatinine mg/dL) + 
                             0.378 * ln(Bilirubin mg/dL) + 
                             1.12 * ln(INR)) + 6.43
        
        Units conversion:
        - Bilirubin: μmol/L → mg/dL (divide by 17.1)
        - Creatinine: μmol/L → mg/dL (divide by 88.4)
        - INR: no conversion needed
        """
        
        # Check required fields
        required_fields = ['total_bilirubin', 'inr', 'creatinine']
        missing = [f for f in required_fields if getattr(latest_lab, f) is None]
        
        if missing:
            self.stdout.write(f'   ⚠ Missing lab values for MELD: {", ".join(missing)}')
            return
        
        try:
            # Convert units for MELD calculation
            # Bilirubin: μmol/L → mg/dL
            bilirubin_umol = float(latest_lab.total_bilirubin)
            bilirubin_mgdl = bilirubin_umol / 17.1
            bilirubin_mgdl = max(bilirubin_mgdl, 1.0)  # MELD uses minimum of 1.0
            
            # Creatinine: μmol/L → mg/dL
            creatinine_umol = float(latest_lab.creatinine)
            creatinine_mgdl = creatinine_umol / 88.4
            creatinine_mgdl = max(creatinine_mgdl, 1.0)  # MELD uses minimum of 1.0
            
            # INR: use as is, minimum 1.0
            inr = max(float(latest_lab.inr), 1.0)
            
            # Calculate MELD score
            meld = (10 * (0.957 * math.log(creatinine_mgdl) + 
                         0.378 * math.log(bilirubin_mgdl) + 
                         1.12 * math.log(inr))) + 6.43
            
            # Adjust for dialysis (if patient is on dialysis, MELD is at least 40)
            dialysis = getattr(latest_lab, 'dialysis_required', False)
            if dialysis:
                meld = max(meld, 40)
            
            # MELD score is capped between 6 and 40
            meld = max(min(meld, 40), 6)
            meld_score = round(meld, 1)
            
            # Calculate MELD-Na if sodium is available
            meld_na = None
            if latest_lab.sodium:
                na = float(latest_lab.sodium)
                # Sodium is capped between 125 and 137 for MELD-Na
                na = max(min(na, 137), 125)
                meld_na = meld + 1.32 * (137 - na) - (0.033 * meld * (137 - na))
                meld_na = max(meld_na, 6)  # MELD-Na minimum is 6
                meld_na = round(meld_na, 1)
            
            if verbose:
                self.stdout.write(f'   📊 MELD calculation:')
                self.stdout.write(f'      Bilirubin: {bilirubin_umol} μmol/L = {bilirubin_mgdl:.1f} mg/dL')
                self.stdout.write(f'      Creatinine: {creatinine_umol} μmol/L = {creatinine_mgdl:.1f} mg/dL')
                self.stdout.write(f'      INR: {inr}')
                self.stdout.write(f'      Dialysis: {dialysis}')
                self.stdout.write(f'      MELD = {meld_score}')
                if meld_na:
                    self.stdout.write(f'      MELD-Na = {meld_na}')
            
            if dry_run:
                self.stdout.write(f'   📊 Would create/update MELD score: {meld_score}' + 
                                 (f' (MELD-Na: {meld_na})' if meld_na else ''))
                results['meld_updated'] += 1
            else:
                # Create or update MELD score
                meld_obj, created = MELDScore.objects.update_or_create(
                    patient=patient,
                    date_assessed=latest_lab.collection_date,
                    defaults={
                        'bilirubin': latest_lab.total_bilirubin,
                        'inr': latest_lab.inr,
                        'creatinine': latest_lab.creatinine,
                        'dialysis': dialysis,
                        'sodium': latest_lab.sodium,
                    }
                )
                
                if created:
                    results['meld_created'] += 1
                    self.stdout.write(f'   ✓ Created MELD score: {meld_score}' +
                                     (f' (MELD-Na: {meld_na})' if meld_na else ''))
                else:
                    results['meld_updated'] += 1
                    self.stdout.write(f'   ✓ Updated MELD score: {meld_score}' +
                                     (f' (MELD-Na: {meld_na})' if meld_na else ''))
        
        except Exception as e:
            results['errors'] += 1
            self.stdout.write(self.style.ERROR(f'   ✗ Error calculating MELD: {str(e)}'))
    
    def _calculate_child_pugh(self, patient, latest_lab, dry_run, verbose, results):
        """
        Calculate Child-Pugh score from laboratory data.
        
        Child-Pugh points:
        - Bilirubin (μmol/L): <34 = 1, 34-51 = 2, >51 = 3
        - Albumin (g/L): >35 = 1, 28-35 = 2, <28 = 3
        - INR: <1.7 = 1, 1.7-2.3 = 2, >2.3 = 3
        - Ascites: none = 1, mild = 2, moderate = 3 (requires manual entry)
        - Encephalopathy: none = 1, grade 1-2 = 2, grade 3-4 = 3 (requires manual entry)
        """
        
        # Check required fields
        required_fields = ['total_bilirubin', 'albumin', 'inr']
        missing = [f for f in required_fields if getattr(latest_lab, f) is None]
        
        if missing:
            self.stdout.write(f'   ⚠ Missing lab values for Child-Pugh: {", ".join(missing)}')
            return
        
        try:
            points = 0
            details = {}
            
            # Bilirubin (μmol/L)
            bili = float(latest_lab.total_bilirubin)
            if bili < 34:
                points += 1
                details['bilirubin'] = f'{bili} μmol/L (1 pt)'
            elif bili <= 51:
                points += 2
                details['bilirubin'] = f'{bili} μmol/L (2 pts)'
            else:
                points += 3
                details['bilirubin'] = f'{bili} μmol/L (3 pts)'
            
            # Albumin (g/L)
            alb = float(latest_lab.albumin)
            if alb > 35:
                points += 1
                details['albumin'] = f'{alb} g/L (1 pt)'
            elif alb >= 28:
                points += 2
                details['albumin'] = f'{alb} g/L (2 pts)'
            else:
                points += 3
                details['albumin'] = f'{alb} g/L (3 pts)'
            
            # INR
            inr = float(latest_lab.inr)
            if inr < 1.7:
                points += 1
                details['inr'] = f'{inr} (1 pt)'
            elif inr <= 2.3:
                points += 2
                details['inr'] = f'{inr} (2 pts)'
            else:
                points += 3
                details['inr'] = f'{inr} (3 pts)'
            
            # Determine class
            if points <= 6:
                child_class = 'A (Well-compensated)'
            elif points <= 9:
                child_class = 'B (Significant functional compromise)'
            else:
                child_class = 'C (Decompensated)'
            
            if verbose:
                self.stdout.write(f'   📊 Child-Pugh calculation:')
                self.stdout.write(f'      {details["bilirubin"]}')
                self.stdout.write(f'      {details["albumin"]}')
                self.stdout.write(f'      {details["inr"]}')
                self.stdout.write(f'      Score: {points} points - Class {child_class}')
                self.stdout.write(f'      Note: Ascites and encephalopathy require manual entry')
            
            if dry_run:
                self.stdout.write(f'   📊 Would create/update Child-Pugh score: {points} points (Class {child_class})')
                results['child_updated'] += 1
            else:
                # Create or update Child-Pugh score
                child_obj, created = ChildPughScore.objects.update_or_create(
                    patient=patient,
                    date_assessed=latest_lab.collection_date,
                    defaults={
                        'bilirubin': latest_lab.total_bilirubin,
                        'albumin': latest_lab.albumin,
                        'inr': latest_lab.inr,
                        'ascites': 'none',  # Default - user should update
                        'encephalopathy': 'none',  # Default - user should update
                    }
                )
                
                if created:
                    results['child_created'] += 1
                    self.stdout.write(f'   ✓ Created Child-Pugh score: {points} points (Class {child_class})')
                    self.stdout.write(f'      ⚠ Update ascites/encephalopathy manually if applicable')
                else:
                    results['child_updated'] += 1
                    self.stdout.write(f'   ✓ Updated Child-Pugh score: {points} points (Class {child_class})')
        
        except Exception as e:
            results['errors'] += 1
            self.stdout.write(self.style.ERROR(f'   ✗ Error calculating Child-Pugh: {str(e)}'))
    
    def _calculate_charlson(self, patient, dry_run, verbose, results):
        """Calculate Charlson Comorbidity Index from existing CharlsonComorbidity data"""
        
        # Get the latest CharlsonComorbidity record for this patient
        charlson_record = patient.charlson_scores.order_by('-date_assessed').first()
        
        if not charlson_record:
            self.stdout.write(f'   ⚠ No Charlson data found - needs manual entry in Scoring → Charlson Comorbidity')
            return
        
        # Calculate score based on the stored comorbidities
        score = 0
        
        # Comorbidity scoring (based on Charlson index)
        comorbidities = {
            'myocardial_infarction': 1,
            'congestive_heart_failure': 1,
            'peripheral_vascular_disease': 1,
            'cerebrovascular_disease': 1,
            'dementia': 1,
            'chronic_pulmonary_disease': 1,
            'connective_tissue_disease': 1,
            'peptic_ulcer_disease': 1,
            'mild_liver_disease': 1,
            'diabetes_without_complications': 1,
            'diabetes_with_complications': 2,
            'hemiplegia': 2,
            'moderate_severe_kidney_disease': 2,
            'solid_tumor': 2,
            'leukemia': 2,
            'lymphoma': 2,
            'moderate_severe_liver_disease': 3,
            'metastatic_solid_tumor': 6,
            'aids': 6,
        }
        
        # Track which comorbidities are present
        active_comorbidities = []
        
        for comorbidity, points in comorbidities.items():
            if hasattr(charlson_record, comorbidity) and getattr(charlson_record, comorbidity):
                score += points
                # Format the comorbidity name for display
                display_name = comorbidity.replace('_', ' ').title()
                active_comorbidities.append(f'{display_name} ({points})')
        
        if verbose:
            if active_comorbidities:
                self.stdout.write(f'   📊 Charlson comorbidities:')
                for c in active_comorbidities:
                    self.stdout.write(f'      - {c}')
                self.stdout.write(f'      Total score: {score}')
            else:
                self.stdout.write(f'   📊 No comorbidities recorded')
        
        if dry_run:
            self.stdout.write(f'   📊 Would update Charlson score: {score}')
            results['charlson_updated'] += 1
        else:
            # The CharlsonComorbidity record already exists, save to update the score property
            charlson_record.save()
            self.stdout.write(f'   ✓ Updated Charlson score: {score}')
            results['charlson_updated'] += 1
    
    def _check_asa(self, patient, verbose):
        """Check if ASA score exists (requires manual entry)"""
        asa_exists = ASAScore.objects.filter(patient=patient).exists()
        
        if asa_exists:
            asa = patient.asa_scores.order_by('-date_assessed').first()
            self.stdout.write(f'   ℹ ASA score: Grade {asa.asa_class}' + 
                            (' (Emergency)' if asa.emergency else ''))
        else:
            self.stdout.write(f'   ⚠ ASA score not set - requires manual entry')

    def _calculate_fibrosis_scores(self, patient, dry_run, verbose, results):
        """Calculate FIB-4 and APRI from latest lab panel"""
        latest_lab = patient.laboratory_panels.order_by('-collection_date').first()
        
        if not latest_lab:
            return
        
        # Check required fields for FIB-4
        fib4_required = ['ast', 'alt', 'platelets']
        missing_fib4 = [f for f in fib4_required if getattr(latest_lab, f) is None]
        
        # Check required fields for APRI
        apri_required = ['ast', 'platelets']
        missing_apri = [f for f in apri_required if getattr(latest_lab, f) is None]
        
        from scoring.models import FibrosisScore
        
        if dry_run:
            if not missing_fib4:
                age = patient.age if patient.age else 0
                ast = latest_lab.ast
                alt = latest_lab.alt
                plt = latest_lab.platelets
                if plt > 0 and alt > 0:
                    fib4 = (age * ast) / (plt * (alt ** 0.5))
                    self.stdout.write(f'   📊 Would create FIB-4: {round(fib4, 2)}')
            if not missing_apri:
                ast = latest_lab.ast
                plt = latest_lab.platelets
                if plt > 0:
                    apri = ((ast / 40) / plt) * 100
                    self.stdout.write(f'   📊 Would create APRI: {round(apri, 2)}')
        else:
            # Create or update fibrosis score
            fibrosis_obj, created = FibrosisScore.objects.update_or_create(
                patient=patient,
                date_assessed=latest_lab.collection_date,
                defaults={'laboratory': latest_lab}
            )
            if created:
                self.stdout.write(f'   ✓ Created Fibrosis Score: FIB-4={fibrosis_obj.fib4_score}, APRI={fibrosis_obj.apri_score}')
            else:
                self.stdout.write(f'   ✓ Updated Fibrosis Score: FIB-4={fibrosis_obj.fib4_score}, APRI={fibrosis_obj.apri_score}')
