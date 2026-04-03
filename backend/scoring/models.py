from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from patients.models import Patient
import math

class MELDScore(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='meld_scores')
    date_assessed = models.DateField(auto_now_add=True)
    bilirubin = models.FloatField(validators=[MinValueValidator(0)], help_text="μmol/L", null=True, blank=True)
    inr = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)
    creatinine = models.FloatField(validators=[MinValueValidator(0)], help_text="μmol/L", null=True, blank=True)
    dialysis = models.BooleanField(default=False)
    sodium = models.FloatField(null=True, blank=True, help_text="mmol/L (for MELD-Na)")
    
    @property
    def score(self):
        """Calculate MELD score with proper None handling"""
        # Check if we have all required values
        if self.bilirubin is None or self.inr is None or self.creatinine is None:
            return None
            
        try:
            bil = max(float(self.bilirubin), 1.0)
            inr_val = max(float(self.inr), 1.0)
            cr = max(float(self.creatinine), 1.0)
            
            meld = 10 * (0.957 * math.log(cr) + 
                         0.378 * math.log(bil) + 
                         1.12 * math.log(inr_val)) + 6.43
            
            if self.dialysis:
                meld = max(meld, 40)
            
            return round(meld, 1)
        except (ValueError, TypeError):
            return None
    
    @property
    def meld_na(self):
        """Calculate MELD-Na score"""
        if self.score is None:
            return None
            
        if self.sodium:
            try:
                meld = self.score
                na = float(self.sodium)
                if na < 125:
                    na = 125
                if na > 137:
                    na = 137
                meld_na = meld + 1.32 * (137 - na) - (0.033 * meld * (137 - na))
                return round(max(meld_na, 6), 1)
            except (ValueError, TypeError):
                return self.score
        return self.score
    
    def save(self, *args, **kwargs):
        # Ensure date_assessed is set if not provided
        if not self.date_assessed:
            from django.utils import timezone
            self.date_assessed = timezone.now().date()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-date_assessed']
    
    def __str__(self):
        score_val = self.score if self.score is not None else "Not calculated"
        return f"MELD: {score_val} - {self.patient}"

class ASAScore(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='asa_scores')
    date_assessed = models.DateField(auto_now_add=True)
    asa_class = models.IntegerField(
        choices=[
            (1, 'ASA I - Healthy patient'),
            (2, 'ASA II - Mild systemic disease'),
            (3, 'ASA III - Severe systemic disease'),
            (4, 'ASA IV - Severe systemic disease that is constant threat to life'),
            (5, 'ASA V - Moribund patient'),
            (6, 'ASA VI - Brain-dead organ donor')
        ],
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    emergency = models.BooleanField(default=False, help_text="Emergency surgery?")
    
    def __str__(self):
        return f"ASA {self.asa_class} - {self.patient}"

class ChildPughScore(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='child_pugh_scores')
    date_assessed = models.DateField(auto_now_add=True)
    
    # Parameters
    bilirubin = models.FloatField(help_text="μmol/L", null=True, blank=True)
    albumin = models.FloatField(help_text="g/L", null=True, blank=True)
    inr = models.FloatField(null=True, blank=True)
    
    ASCITES_CHOICES = [
        ('none', 'None'),
        ('mild', 'Mild (diuretic responsive)'),
        ('moderate', 'Moderate/Severe (diuretic refractory)')
    ]
    ascites = models.CharField(max_length=20, choices=ASCITES_CHOICES, default='none')
    
    ENCEPHALOPATHY_CHOICES = [
        ('none', 'None'),
        ('grade1_2', 'Grade I-II (mild)'),
        ('grade3_4', 'Grade III-IV (severe)')
    ]
    encephalopathy = models.CharField(max_length=20, choices=ENCEPHALOPATHY_CHOICES, default='none')
    
    @property
    def score(self):
        """Calculate Child-Pugh score with proper None handling"""
        if self.bilirubin is None or self.albumin is None or self.inr is None:
            return None
            
        points = 0
        
        # Bilirubin
        if self.bilirubin < 34:
            points += 1
        elif self.bilirubin < 51:
            points += 2
        else:
            points += 3
        
        # Albumin
        if self.albumin > 35:
            points += 1
        elif self.albumin > 28:
            points += 2
        else:
            points += 3
        
        # INR
        if self.inr < 1.7:
            points += 1
        elif self.inr < 2.3:
            points += 2
        else:
            points += 3
        
        # Ascites
        if self.ascites == 'none':
            points += 1
        elif self.ascites == 'mild':
            points += 2
        else:
            points += 3
        
        # Encephalopathy
        if self.encephalopathy == 'none':
            points += 1
        elif self.encephalopathy == 'grade1_2':
            points += 2
        else:
            points += 3
        
        return points
    
    @property
    def class_grade(self):
        score = self.score
        if score is None:
            return 'Not calculated'
        if score <= 6:
            return 'A (Well-compensated disease)'
        elif score <= 9:
            return 'B (Significant functional compromise)'
        else:
            return 'C (Decompensated disease)'
    
    def __str__(self):
        score_val = self.score if self.score is not None else "Not calculated"
        return f"Child-Pugh {score_val} - {self.patient}"

class CharlsonComorbidity(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='charlson_scores')
    date_assessed = models.DateField(auto_now_add=True)
    
    # Charlson components
    myocardial_infarction = models.BooleanField(default=False)
    congestive_heart_failure = models.BooleanField(default=False)
    peripheral_vascular_disease = models.BooleanField(default=False)
    cerebrovascular_disease = models.BooleanField(default=False)
    dementia = models.BooleanField(default=False)
    chronic_pulmonary_disease = models.BooleanField(default=False)
    connective_tissue_disease = models.BooleanField(default=False)
    peptic_ulcer_disease = models.BooleanField(default=False)
    mild_liver_disease = models.BooleanField(default=False)
    moderate_severe_liver_disease = models.BooleanField(default=False)
    diabetes_without_complications = models.BooleanField(default=False)
    diabetes_with_complications = models.BooleanField(default=False)
    hemiplegia = models.BooleanField(default=False)
    moderate_severe_kidney_disease = models.BooleanField(default=False)
    solid_tumor = models.BooleanField(default=False, help_text="Non-metastatic solid tumor")
    leukemia = models.BooleanField(default=False)
    lymphoma = models.BooleanField(default=False)
    metastatic_solid_tumor = models.BooleanField(default=False)
    aids = models.BooleanField(default=False)
    
    @property
    def score(self):
        total = 0
        
        # Myocardial infarct (1)
        if self.myocardial_infarction:
            total += 1
        
        # Congestive heart failure (1)
        if self.congestive_heart_failure:
            total += 1
        
        # Peripheral vascular disease (1)
        if self.peripheral_vascular_disease:
            total += 1
        
        # Cerebrovascular disease (1)
        if self.cerebrovascular_disease:
            total += 1
        
        # Dementia (1)
        if self.dementia:
            total += 1
        
        # Chronic pulmonary disease (1)
        if self.chronic_pulmonary_disease:
            total += 1
        
        # Connective tissue disease (1)
        if self.connective_tissue_disease:
            total += 1
        
        # Peptic ulcer disease (1)
        if self.peptic_ulcer_disease:
            total += 1
        
        # Mild liver disease (1)
        if self.mild_liver_disease:
            total += 1
        
        # Diabetes without complications (1)
        if self.diabetes_without_complications:
            total += 1
        
        # Diabetes with complications (2)
        if self.diabetes_with_complications:
            total += 2
        
        # Hemiplegia (2)
        if self.hemiplegia:
            total += 2
        
        # Moderate or severe kidney disease (2)
        if self.moderate_severe_kidney_disease:
            total += 2
        
        # Solid tumor (2)
        if self.solid_tumor:
            total += 2
        
        # Leukemia (2)
        if self.leukemia:
            total += 2
        
        # Lymphoma (2)
        if self.lymphoma:
            total += 2
        
        # Moderate or severe liver disease (3)
        if self.moderate_severe_liver_disease:
            total += 3
        
        # Metastatic solid tumor (6)
        if self.metastatic_solid_tumor:
            total += 6
        
        # AIDS (6)
        if self.aids:
            total += 6
        
        return total
    
    def __str__(self):
        return f"Charlson: {self.score} - {self.patient}"

class FibrosisScore(models.Model):
    """
    Non-invasive liver fibrosis scores (FIB-4 and APRI)
    Reference: Sterling RK, et al. Development of a simple noninvasive index to predict significant fibrosis
    """
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='fibrosis_scores')
    date_assessed = models.DateField(auto_now_add=True)
    laboratory = models.ForeignKey('laboratory.LaboratoryPanel', on_delete=models.CASCADE, null=True, blank=True)
    
    # FIB-4 Index
    # Formula: (Age × AST) / (Platelets × √ALT)
    fib4_score = models.FloatField(null=True, blank=True, help_text="FIB-4 score")
    
    # APRI Score (AST to Platelet Ratio Index)
    # Formula: (AST/ULN) / Platelets × 100
    apri_score = models.FloatField(null=True, blank=True, help_text="APRI score")
    
    # Interpretations
    FIB4_CATEGORIES = [
        ('low', 'Low risk of advanced fibrosis (<1.45)'),
        ('intermediate', 'Intermediate risk (1.45-3.25)'),
        ('high', 'High risk of advanced fibrosis (>3.25)'),
    ]
    fib4_category = models.CharField(max_length=20, choices=FIB4_CATEGORIES, null=True, blank=True)
    
    APRI_CATEGORIES = [
        ('low', 'Low risk of cirrhosis (<0.5)'),
        ('intermediate', 'Intermediate risk (0.5-1.5)'),
        ('high', 'High risk of cirrhosis (>1.5)'),
    ]
    apri_category = models.CharField(max_length=20, choices=APRI_CATEGORIES, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_assessed']
        verbose_name_plural = "Fibrosis Scores"
    
    def calculate_fib4(self, age, ast, alt, platelets):
        """Calculate FIB-4 score"""
        if all([age, ast, platelets, alt]) and platelets > 0 and alt > 0:
            try:
                fib4 = (age * ast) / (platelets * (alt ** 0.5))
                return round(fib4, 2)
            except (ValueError, ZeroDivisionError):
                pass
        return None
    
    def calculate_apri(self, ast, platelets, ast_uln=40):
        """Calculate APRI score (AST ULN = 40 U/L)"""
        if all([ast, platelets]) and platelets > 0:
            try:
                ast_ratio = ast / ast_uln
                apri = (ast_ratio / platelets) * 100
                return round(apri, 2)
            except (ValueError, ZeroDivisionError):
                pass
        return None
    
    def get_fib4_category(self, fib4):
        if fib4:
            if fib4 < 1.45:
                return 'low'
            elif fib4 <= 3.25:
                return 'intermediate'
            else:
                return 'high'
        return None
    
    def get_apri_category(self, apri):
        if apri:
            if apri < 0.5:
                return 'low'
            elif apri <= 1.5:
                return 'intermediate'
            else:
                return 'high'
        return None
    
    def save(self, *args, **kwargs):
        # Auto-calculate if lab data is available
        if self.laboratory:
            # Get patient age
            age = self.patient.age if self.patient.age else 0
            
            # Calculate FIB-4
            self.fib4_score = self.calculate_fib4(
                age,
                self.laboratory.ast,
                self.laboratory.alt,
                self.laboratory.platelets
            )
            self.fib4_category = self.get_fib4_category(self.fib4_score)
            
            # Calculate APRI
            self.apri_score = self.calculate_apri(
                self.laboratory.ast,
                self.laboratory.platelets
            )
            self.apri_category = self.get_apri_category(self.apri_score)
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"FIB-4: {self.fib4_score}, APRI: {self.apri_score} - {self.patient}"


class NutritionalRiskIndex(models.Model):
    """
    Nutritional Risk Index for surgical outcomes
    Reference: The Veterans Affairs Total Parenteral Nutrition Cooperative Study Group
    """
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='nri_scores')
    date_assessed = models.DateField(auto_now_add=True)
    
    # NRI = (1.519 × albumin g/L) + (41.7 × weight loss ratio)
    albumin_g_l = models.FloatField(help_text="Serum albumin (g/L)")
    usual_weight_kg = models.FloatField(help_text="Usual weight before illness (kg)")
    current_weight_kg = models.FloatField(help_text="Current weight (kg)")
    
    nri_score = models.FloatField(null=True, blank=True)
    
    NRI_CATEGORIES = [
        ('severe', 'Severe malnutrition (<83.5)'),
        ('moderate', 'Moderate malnutrition (83.5-97.5)'),
        ('mild', 'Mild malnutrition (97.5-100)'),
        ('normal', 'Normal nutrition (>100)'),
    ]
    category = models.CharField(max_length=20, choices=NRI_CATEGORIES, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_assessed']
        verbose_name_plural = "Nutritional Risk Indices"
    
    def calculate_nri(self):
        if self.albumin_g_l and self.usual_weight_kg and self.current_weight_kg:
            weight_ratio = self.current_weight_kg / self.usual_weight_kg if self.usual_weight_kg > 0 else 1
            nri = (1.519 * self.albumin_g_l) + (41.7 * weight_ratio)
            return round(nri, 1)
        return None
    
    def get_category(self, nri):
        if nri:
            if nri < 83.5:
                return 'severe'
            elif nri < 97.5:
                return 'moderate'
            elif nri < 100:
                return 'mild'
            else:
                return 'normal'
        return None
    
    def save(self, *args, **kwargs):
        self.nri_score = self.calculate_nri()
        self.category = self.get_category(self.nri_score)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"NRI: {self.nri_score} - {self.patient}"

class SarcopeniaAssessment(models.Model):
    """
    Sarcopenia assessment using CT-based muscle measurements
    Reference: Prado CM, et al. Sarcopenia as a determinant of chemotherapy toxicity
    """
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='sarcopenia_assessments')
    date_assessed = models.DateField(auto_now_add=True)
    
    # CT measurements at L3 vertebra level
    skeletal_muscle_index_cm2_m2 = models.FloatField(
        null=True, blank=True,
        help_text="Skeletal muscle index at L3 (cm²/m²) - Sarcopenia cutoff: M<55, F<39"
    )
    psoas_muscle_area_cm2 = models.FloatField(
        null=True, blank=True,
        help_text="Psoas muscle area at L3 (cm²)"
    )
    visceral_fat_area_cm2 = models.FloatField(
        null=True, blank=True,
        help_text="Visceral fat area at L3 (cm²)"
    )
    subcutaneous_fat_area_cm2 = models.FloatField(
        null=True, blank=True,
        help_text="Subcutaneous fat area at L3 (cm²)"
    )
    
    # Patient gender (for cutoff determination)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, help_text="Patient gender for cutoff determination")
    
    is_sarcopenic = models.BooleanField(
        default=False,
        help_text="Based on SMI cutoffs: Male <55 cm²/m², Female <39 cm²/m²"
    )
    
    ct_slice_location = models.CharField(
        max_length=50, blank=True,
        help_text="CT slice location (e.g., L3 vertebra)"
    )
    ct_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-ct_date']
        verbose_name_plural = "Sarcopenia Assessments"
    
    def check_sarcopenia(self):
        """Check sarcopenia based on SMI cutoffs (Prado 2008)"""
        if self.skeletal_muscle_index_cm2_m2:
            if self.gender == 'M' and self.skeletal_muscle_index_cm2_m2 < 55:
                return True
            elif self.gender == 'F' and self.skeletal_muscle_index_cm2_m2 < 39:
                return True
        return False
    
    def save(self, *args, **kwargs):
        self.is_sarcopenic = self.check_sarcopenia()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Sarcopenia: {'Yes' if self.is_sarcopenic else 'No'} - {self.patient}"
