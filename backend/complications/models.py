from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from clinical.models import SurgicalProcedure

class GeneralComplication(models.Model):
    """General postoperative complications (non-organ specific)"""
    surgical_procedure = models.ForeignKey(SurgicalProcedure, on_delete=models.CASCADE, related_name='general_complications')
    
    COMPLICATION_TYPES = [
        ('surgical_site_infection', 'Surgical Site Infection'),
        ('pneumonia', 'Pneumonia'),
        ('uti', 'Urinary Tract Infection'),
        ('sepsis', 'Sepsis'),
        ('dvt', 'Deep Vein Thrombosis'),
        ('pe', 'Pulmonary Embolism'),
        ('mi', 'Myocardial Infarction'),
        ('stroke', 'Stroke'),
        ('aki', 'Acute Kidney Injury'),
        ('delirium', 'Delirium'),
        ('ileus', 'Prolonged Ileus (>5 days)'),
        ('bleeding', 'Postoperative Bleeding requiring transfusion'),
        ('anastomotic_leak', 'Anastomotic Leak'),
        ('bile_leak_grade_a', 'Bile Leak - Grade A (Managed conservatively)'),
        ('bile_leak_grade_b', 'Bile Leak - Grade B (Requires intervention)'),
        ('bile_leak_grade_c', 'Bile Leak - Grade C (Reoperation required)'),
        ('other', 'Other'),
    ]
    
    complication_type = models.CharField(max_length=50, choices=COMPLICATION_TYPES)
    
    # Timing
    onset_days = models.IntegerField(help_text="Postoperative day of onset (0 for intraoperative)")
    resolved = models.BooleanField(default=False)
    resolved_days = models.IntegerField(null=True, blank=True, help_text="Postoperative day of resolution")
    
    # Severity - Clavien-Dindo classification
    CLAVIEN_CHOICES = [
        (1, 'Grade I - Any deviation from normal course without need for treatment'),
        (2, 'Grade II - Pharmacologic treatment required'),
        (3, 'Grade IIIa - Intervention without general anesthesia'),
        (4, 'Grade IIIb - Intervention with general anesthesia'),
        (5, 'Grade IVa - Single organ dysfunction'),
        (6, 'Grade IVb - Multiorgan dysfunction'),
        (7, 'Grade V - Death of patient'),
    ]
    clavien_grade = models.IntegerField(choices=CLAVIEN_CHOICES)
    
    # Bile leak specific fields
    drain_bilirubin = models.FloatField(null=True, blank=True, help_text="Drain bilirubin (μmol/L)")
    drain_bilirubin_ratio = models.FloatField(null=True, blank=True, help_text="Drain/Serum bilirubin ratio")
    intervention_required = models.BooleanField(default=False)
    intervention_type = models.CharField(max_length=100, blank=True, help_text="e.g., ERCP, PTBD, Surgery")
    
    # Management
    treatment = models.TextField(blank=True, help_text="Describe treatment provided")
    reoperation_required = models.BooleanField(default=False)
    reoperation_details = models.TextField(blank=True)
    
    # Outcome
    resolved_completely = models.BooleanField(default=True, help_text="Did the complication resolve completely?")
    sequelae = models.TextField(blank=True, help_text="Any long-term sequelae")
    details = models.TextField(blank=True, help_text="Specific details about the complication")
    
    def __str__(self):
        return f"{self.get_complication_type_display()} - POD {self.onset_days} (Grade {self.clavien_grade})"

class PancreaticComplication(models.Model):
    """Pancreas-specific complications"""
    surgical_procedure = models.ForeignKey(SurgicalProcedure, on_delete=models.CASCADE, related_name='pancreatic_complications')
    
    COMPLICATION_TYPES = [
        ('popf_grade_b', 'POPF - Grade B (Requires intervention)'),
        ('popf_grade_c', 'POPF - Grade C (Severe, reoperation/death)'),
        ('delayed_gastric_emptying', 'Delayed Gastric Emptying'),
        ('post_pancreatectomy_hemorrhage', 'Post-pancreatectomy Hemorrhage'),
        ('pancreatitis', 'Acute Pancreatitis'),
        ('pancreatic_necrosis', 'Pancreatic Necrosis'),
        ('other', 'Other'),
    ]
    
    complication_type = models.CharField(max_length=50, choices=COMPLICATION_TYPES)
    
    # Timing
    onset_days = models.IntegerField(help_text="Postoperative day of onset (0 for intraoperative)")
    resolved = models.BooleanField(default=False)
    resolved_days = models.IntegerField(null=True, blank=True, help_text="Postoperative day of resolution")
    
    # Severity - Clavien-Dindo classification
    CLAVIEN_CHOICES = [
        (1, 'Grade I - Any deviation from normal course without need for treatment'),
        (2, 'Grade II - Pharmacologic treatment required'),
        (3, 'Grade IIIa - Intervention without general anesthesia'),
        (4, 'Grade IIIb - Intervention with general anesthesia'),
        (5, 'Grade IVa - Single organ dysfunction'),
        (6, 'Grade IVb - Multiorgan dysfunction'),
        (7, 'Grade V - Death of patient'),
    ]
    clavien_grade = models.IntegerField(choices=CLAVIEN_CHOICES)
    
    # POPF specific
    popf_drain_amylase = models.FloatField(null=True, blank=True, help_text="Drain amylase (U/L)")
    drain_amylase_pod1 = models.FloatField(null=True, blank=True, help_text="Drain amylase on POD 1 (U/L)")
    drain_amylase_pod3 = models.FloatField(null=True, blank=True, help_text="Drain amylase on POD 3 (U/L)")
    drain_output_ml = models.IntegerField(null=True, blank=True, help_text="Daily drain output (mL)")
    
    # Hemorrhage specific
    hemoglobin_drop = models.FloatField(null=True, blank=True, help_text="Drop in hemoglobin (g/L)")
    transfusion_units = models.IntegerField(null=True, blank=True, help_text="Units of blood transfused")
    intervention_type = models.CharField(max_length=100, blank=True, help_text="e.g., Angiography, Surgery")
    
    # Delayed gastric emptying
    nasogastric_days = models.IntegerField(null=True, blank=True, help_text="Days with nasogastric tube")
    
    # Management
    treatment = models.TextField(blank=True, help_text="Describe treatment provided")
    reoperation_required = models.BooleanField(default=False)
    reoperation_details = models.TextField(blank=True)
    
    # Outcome
    resolved_completely = models.BooleanField(default=True, help_text="Did the complication resolve completely?")
    sequelae = models.TextField(blank=True, help_text="Any long-term sequelae")
    details = models.TextField(blank=True, help_text="Specific details about the complication")
    
    def __str__(self):
        return f"{self.get_complication_type_display()} - POD {self.onset_days} (Grade {self.clavien_grade})"

class LiverComplication(models.Model):
    """Liver-specific complications"""
    surgical_procedure = models.ForeignKey(SurgicalProcedure, on_delete=models.CASCADE, related_name='liver_complications')
    
    COMPLICATION_TYPES = [
        ('post_hepatectomy_liver_failure', 'Post-hepatectomy Liver Failure'),
        ('ascites', 'Ascites'),
        ('portal_vein_thrombosis', 'Portal Vein Thrombosis'),
        ('hepatic_artery_thrombosis', 'Hepatic Artery Thrombosis'),
        ('hepatic_vein_obstruction', 'Hepatic Vein Obstruction'),
        ('other', 'Other'),
    ]
    
    complication_type = models.CharField(max_length=50, choices=COMPLICATION_TYPES)
    
    # Timing
    onset_days = models.IntegerField(help_text="Postoperative day of onset (0 for intraoperative)")
    resolved = models.BooleanField(default=False)
    resolved_days = models.IntegerField(null=True, blank=True, help_text="Postoperative day of resolution")
    
    # Severity - Clavien-Dindo classification
    CLAVIEN_CHOICES = [
        (1, 'Grade I - Any deviation from normal course without need for treatment'),
        (2, 'Grade II - Pharmacologic treatment required'),
        (3, 'Grade IIIa - Intervention without general anesthesia'),
        (4, 'Grade IIIb - Intervention with general anesthesia'),
        (5, 'Grade IVa - Single organ dysfunction'),
        (6, 'Grade IVb - Multiorgan dysfunction'),
        (7, 'Grade V - Death of patient'),
    ]
    clavien_grade = models.IntegerField(choices=CLAVIEN_CHOICES)
    
    # Liver failure specific (ISGLS criteria)
    bilirubin_pod5 = models.FloatField(null=True, blank=True, help_text="Bilirubin on POD 5 (μmol/L)")
    inr_pod5 = models.FloatField(null=True, blank=True, help_text="INR on POD 5")
    
    # Ascites specific
    ascites_volume_ml = models.IntegerField(null=True, blank=True, help_text="Daily ascites output (mL)")
    diuretic_required = models.BooleanField(default=False)
    
    # Management
    treatment = models.TextField(blank=True, help_text="Describe treatment provided")
    reoperation_required = models.BooleanField(default=False)
    reoperation_details = models.TextField(blank=True)
    
    # Outcome
    resolved_completely = models.BooleanField(default=True, help_text="Did the complication resolve completely?")
    sequelae = models.TextField(blank=True, help_text="Any long-term sequelae")
    details = models.TextField(blank=True, help_text="Specific details about the complication")
    
    def __str__(self):
        return f"{self.get_complication_type_display()} - POD {self.onset_days} (Grade {self.clavien_grade})"
