from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import date
from django.contrib.auth.models import User
from hpb_registry.mixins import AuditMixin
from medical_codes.models import Diagnosis


class Patient(AuditMixin):
    """Patient model for HPB Surgery Registry"""
    
    # Patient identifiers
    patient_id = models.CharField(
        max_length=50, 
        unique=True, 
        help_text="Unique patient identifier (e.g., hospital ID)"
    )
    jmbg = models.CharField(
        max_length=13, 
        unique=True, 
        blank=True, 
        null=True,
        help_text="Unique Master Citizen Number (JMBG)"
    )
    mrn = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="Medical Record Number"
    )
    
    # Personal information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    
    # Contact information
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default='Serbia')
    
    # Medical information
    main_diagnosis = models.ForeignKey(
        Diagnosis, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='patients',
        help_text="Primary ICD-10 diagnosis"
    )
    
    SMOKING_CHOICES = [
        ('never', 'Never smoked'),
        ('former', 'Former smoker'),
        ('current', 'Current smoker'),
    ]
    smoking_status = models.CharField(
        max_length=20, 
        choices=SMOKING_CHOICES, 
        blank=True
    )
    
    # Comorbidities
    diabetes = models.BooleanField(default=False)
    hypertension = models.BooleanField(default=False)
    copd = models.BooleanField(default=False, help_text="Chronic Obstructive Pulmonary Disease")
    coronary_artery_disease = models.BooleanField(default=False)
    chronic_kidney_disease = models.BooleanField(default=False)
    
    # Anthropometric data
    height = models.FloatField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0)],
        help_text="Height in cm"
    )
    weight = models.FloatField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0)],
        help_text="Weight in kg"
    )
    
    # Status tracking
    STATUS_CHOICES = [
        ('active', 'Active Follow-up'),
        ('deceased', 'Deceased'),
        ('transferred', 'Transferred to other institution'),
        ('lost', 'Lost to Follow-up'),
        ('inactive', 'Inactive'),
    ]
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active',
        help_text="Current patient status"
    )
    
    # Date tracking
    date_of_death = models.DateField(null=True, blank=True)
    
    # Clinical notes
    clinical_notes = models.TextField(blank=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient_id'], name='patient_id_idx'),
            models.Index(fields=['last_name', 'first_name'], name='name_idx'),
            models.Index(fields=['status'], name='status_idx'),
            models.Index(fields=['created_at'], name='created_at_idx'),
        ]
    
    def __str__(self):
        return f"{self.patient_id} - {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        """Return patient's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calculate patient's age based on date of birth"""
        if self.date_of_birth:
            today = date.today()
            age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
            return age
        return None
    
    @property
    def bmi(self):
        """Calculate Body Mass Index"""
        if self.height and self.weight and self.height > 0:
            height_m = self.height / 100
            bmi = self.weight / (height_m ** 2)
            return round(bmi, 1)
        return None
    
    @property
    def bmi_category(self):
        """Get BMI category"""
        bmi = self.bmi
        if bmi:
            if bmi < 18.5:
                return 'Underweight'
            elif bmi < 25:
                return 'Normal weight'
            elif bmi < 30:
                return 'Overweight'
            else:
                return 'Obese'
        return None
    
    def clean(self):
        """Validate patient data"""
        errors = {}
        
        # Validate date of birth
        if self.date_of_birth and self.date_of_birth > date.today():
            errors['date_of_birth'] = 'Date of birth cannot be in the future'
        
        # Validate date of death
        if self.date_of_death:
            if self.date_of_death > date.today():
                errors['date_of_death'] = 'Date of death cannot be in the future'
            if self.date_of_birth and self.date_of_death < self.date_of_birth:
                errors['date_of_death'] = 'Date of death cannot be before date of birth'
                
        # Validate JMBG format (if provided)
        if self.jmbg:
            if not self.jmbg.isdigit():
                errors['jmbg'] = 'JMBG must contain only digits'
            if len(self.jmbg) != 13:
                errors['jmbg'] = 'JMBG must be exactly 13 digits'
        
        # Validate BMI
        if self.height and self.weight:
            if self.height < 50 or self.height > 250:
                errors['height'] = 'Height must be between 50 and 250 cm'
            if self.weight < 10 or self.weight > 500:
                errors['weight'] = 'Weight must be between 10 and 500 kg'
            
            bmi = self.bmi
            if bmi and (bmi < 10 or bmi > 50):
                errors['bmi'] = f'Invalid BMI calculated: {bmi:.1f}. Please check height and weight.'
        
        # Validate status consistency with date of death
        if self.status == 'deceased' and not self.date_of_death:
            errors['date_of_death'] = 'Date of death is required when status is "Deceased"'
        
        if self.date_of_death and self.status != 'deceased':
            errors['status'] = 'Status must be "Deceased" when date of death is provided'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Save patient with validation"""
        self.clean()
        super().save(*args, **kwargs)
