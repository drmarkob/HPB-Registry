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
