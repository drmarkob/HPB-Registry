from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from patients.models import Patient

class LaboratoryPanel(models.Model):
    """Comprehensive laboratory panel for HPB patients"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='laboratory_panels')
    collection_date = models.DateField()
    collection_time = models.TimeField(null=True, blank=True)
    
    # Timing relative to treatment
    TIMING_CHOICES = [
        ('preoperative', 'Preoperative'),
        ('postoperative_day1', 'Postoperative Day 1'),
        ('postoperative_day3', 'Postoperative Day 3'),
        ('postoperative_day5', 'Postoperative Day 5'),
        ('postoperative_day7', 'Postoperative Day 7'),
        ('pre_chemotherapy', 'Pre-chemotherapy'),
        ('post_chemotherapy', 'Post-chemotherapy'),
        ('follow_up', 'Follow-up'),
    ]
    timing = models.CharField(max_length=30, choices=TIMING_CHOICES)
    
    # Complete Blood Count (CBC)
    hemoglobin = models.FloatField(null=True, blank=True, help_text="g/L")
    hematocrit = models.FloatField(null=True, blank=True, help_text="%")
    wbc = models.FloatField(null=True, blank=True, help_text="x10^9/L")
    neutrophils = models.FloatField(null=True, blank=True, help_text="x10^9/L")
    lymphocytes = models.FloatField(null=True, blank=True, help_text="x10^9/L")
    monocytes = models.FloatField(null=True, blank=True, help_text="x10^9/L")
    platelets = models.FloatField(null=True, blank=True, help_text="x10^9/L")
    
    # Liver function tests
    alt = models.FloatField(null=True, blank=True, help_text="U/L (Alanine aminotransferase)")
    ast = models.FloatField(null=True, blank=True, help_text="U/L (Aspartate aminotransferase)")
    alp = models.FloatField(null=True, blank=True, help_text="U/L (Alkaline phosphatase)")
    ggt = models.FloatField(null=True, blank=True, help_text="U/L (Gamma-glutamyl transferase)")
    total_bilirubin = models.FloatField(null=True, blank=True, help_text="μmol/L")
    direct_bilirubin = models.FloatField(null=True, blank=True, help_text="μmol/L")
    indirect_bilirubin = models.FloatField(null=True, blank=True, help_text="μmol/L")
    total_protein = models.FloatField(null=True, blank=True, help_text="g/L")
    albumin = models.FloatField(null=True, blank=True, help_text="g/L")
    
    # Coagulation
    inr = models.FloatField(null=True, blank=True)
    pt = models.FloatField(null=True, blank=True, help_text="seconds (Prothrombin time)")
    ptt = models.FloatField(null=True, blank=True, help_text="seconds (Partial thromboplastin time)")
    
    # Renal function
    creatinine = models.FloatField(null=True, blank=True, help_text="μmol/L")
    urea = models.FloatField(null=True, blank=True, help_text="mmol/L")
    egfr = models.FloatField(null=True, blank=True, help_text="mL/min/1.73m² (eGFR)")
    
    # Electrolytes
    sodium = models.FloatField(null=True, blank=True, help_text="mmol/L")
    potassium = models.FloatField(null=True, blank=True, help_text="mmol/L")
    chloride = models.FloatField(null=True, blank=True, help_text="mmol/L")
    calcium = models.FloatField(null=True, blank=True, help_text="mmol/L")
    magnesium = models.FloatField(null=True, blank=True, help_text="mmol/L")
    phosphate = models.FloatField(null=True, blank=True, help_text="mmol/L")
    
    # Inflammatory markers
    crp = models.FloatField(null=True, blank=True, help_text="mg/L (C-reactive protein)")
    esr = models.FloatField(null=True, blank=True, help_text="mm/h (Erythrocyte sedimentation rate)")
    procalcitonin = models.FloatField(null=True, blank=True, help_text="ng/mL")
    
    # Nutritional markers
    prealbumin = models.FloatField(null=True, blank=True, help_text="mg/L")
    transferrin = models.FloatField(null=True, blank=True, help_text="g/L")
    
    # Comments
    comments = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-collection_date']
        verbose_name_plural = "Laboratory panels"
    
    def __str__(self):
        return f"Labs: {self.patient} - {self.collection_date} ({self.get_timing_display()})"
    
    @property
    def nlr(self):
        """Neutrophil to Lymphocyte Ratio"""
        if self.neutrophils and self.lymphocytes and self.lymphocytes > 0:
            return round(self.neutrophils / self.lymphocytes, 2)
        return None
    
    @property
    def plr(self):
        """Platelet to Lymphocyte Ratio"""
        if self.platelets and self.lymphocytes and self.lymphocytes > 0:
            return round(self.platelets / self.lymphocytes, 2)
        return None
    
    @property
    def apr(self):
        """AST to Platelet Ratio Index (APRI)"""
        if self.ast and self.platelets and self.platelets > 0:
            ast_ratio = self.ast / 40  # Upper limit of normal
            return round((ast_ratio / self.platelets) * 100, 2)
        return None

class TumorMarkerPanel(models.Model):
    """Tumor markers for HPB oncology"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='tumor_markers')
    collection_date = models.DateField()
    
    TIMING_CHOICES = [
        ('baseline', 'Baseline (Pre-treatment)'),
        ('during_treatment', 'During Treatment'),
        ('post_treatment', 'Post-treatment'),
        ('follow_up', 'Follow-up'),
        ('recurrence', 'At Recurrence'),
    ]
    timing = models.CharField(max_length=20, choices=TIMING_CHOICES)
    
    # Common HPB tumor markers
    ca19_9 = models.FloatField(null=True, blank=True, help_text="U/mL (Carbohydrate antigen 19-9)")
    
    cea = models.FloatField(null=True, blank=True, help_text="ng/mL (Carcinoembryonic antigen)")
    
    afp = models.FloatField(null=True, blank=True, help_text="ng/mL (Alpha-fetoprotein)")
    
    # Pancreatic neuroendocrine tumors
    chromogranin_a = models.FloatField(null=True, blank=True, help_text="ng/mL (CgA)")
    
    neuron_specific_enolase = models.FloatField(null=True, blank=True, help_text="ng/mL (NSE)")
    
    pancreastatin = models.FloatField(null=True, blank=True, help_text="pg/mL")
    
    # Specific for NETs
    serotonin = models.FloatField(null=True, blank=True, help_text="nmol/L")
    hiaa_5 = models.FloatField(null=True, blank=True, help_text="μmol/24h (5-HIAA in urine)")  # Changed from 5_hiaa
    
    # Biliary tract
    ca_50 = models.FloatField(null=True, blank=True, help_text="U/mL")
    ca_242 = models.FloatField(null=True, blank=True, help_text="U/mL")
    
    # Gastric and other
    ca_125 = models.FloatField(null=True, blank=True, help_text="U/mL")
    ca_15_3 = models.FloatField(null=True, blank=True, help_text="U/mL")
    ca_72_4 = models.FloatField(null=True, blank=True, help_text="U/mL")
    
    # Liver specific
    des_gamma_carboxy_prothrombin = models.FloatField(null=True, blank=True, help_text="mAU/mL (DCP)")
    golgi_protein_73 = models.FloatField(null=True, blank=True, help_text="ng/mL (GP73)")
    
    # Notes
    notes = models.TextField(blank=True, help_text="Any additional notes about marker results")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-collection_date']
    
    def __str__(self):
        return f"Tumor markers: {self.patient} - {self.collection_date}"
    
    @property
    def ca19_9_ratio(self):
        """CA19-9 ratio to upper limit of normal"""
        if self.ca19_9 and self.ca19_9_upper_limit and self.ca19_9_upper_limit > 0:
            return round(self.ca19_9 / self.ca19_9_upper_limit, 2)
        return None
    
    @property
    def cea_ratio(self):
        """CEA ratio to upper limit of normal"""
        if self.cea and self.cea_upper_limit and self.cea_upper_limit > 0:
            return round(self.cea / self.cea_upper_limit, 2)
        return None

class MicrobiologyCulture(models.Model):
    """Microbiology cultures for infections"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='cultures')
    collection_date = models.DateField()
    
    SPECIMEN_TYPES = [
        ('blood', 'Blood Culture'),
        ('drain_fluid', 'Drain Fluid'),
        ('bile', 'Bile'),
        ('wound', 'Wound Swab'),
        ('urine', 'Urine'),
        ('sputum', 'Sputum'),
        ('peritoneal_fluid', 'Peritoneal Fluid'),
    ]
    specimen_type = models.CharField(max_length=20, choices=SPECIMEN_TYPES)
    
    organism = models.CharField(max_length=200, help_text="Microorganism identified")
    antibiotic_sensitivity = models.TextField(blank=True, help_text="List sensitive antibiotics")
    resistant_antibiotics = models.TextField(blank=True, help_text="List resistant antibiotics")
    
    # Clinical context
    clinical_significance = models.BooleanField(default=True, help_text="Considered clinically significant?")
    infection_site = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.organism} - {self.patient} ({self.specimen_type})"
