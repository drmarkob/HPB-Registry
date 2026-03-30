from django.db import models

class Diagnosis(models.Model):
    """Main diagnoses for HPB surgery with ICD-10 codes"""
    icd10_code = models.CharField(max_length=10, unique=True, help_text="ICD-10 code (e.g., C22.0)")
    diagnosis_name = models.CharField(max_length=200, help_text="Diagnosis name")
    category = models.CharField(max_length=50, choices=[
        ('liver_malignant', 'Liver - Malignant'),
        ('liver_benign', 'Liver - Benign'),
        ('pancreas_malignant', 'Pancreas - Malignant'),
        ('pancreas_benign', 'Pancreas - Benign'),
        ('biliary_malignant', 'Biliary - Malignant'),
        ('biliary_benign', 'Biliary - Benign'),
        ('other', 'Other'),
    ])
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category', 'diagnosis_name']
        verbose_name_plural = "Diagnoses"
    
    def __str__(self):
        return f"{self.icd10_code} - {self.diagnosis_name}"

class HistologyType(models.Model):
    """Histological types for HPB tumors"""
    name = models.CharField(max_length=200, unique=True, help_text="Histology type name")
    category = models.CharField(max_length=50, choices=[
        ('malignant', 'Malignant'),
        ('benign', 'Benign'),
        ('premalignant', 'Premalignant'),
    ])
    organ_system = models.CharField(max_length=50, choices=[
        ('liver', 'Liver'),
        ('pancreas', 'Pancreas'),
        ('biliary', 'Biliary'),
        ('general', 'General'),
    ], default='general')
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name_plural = "Histology Types"
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
