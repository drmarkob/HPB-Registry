from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from patients.models import Patient
from medical_codes.models import Diagnosis, HistologyType  # Comment temporarily

class MolecularMarkers(models.Model):
    """Molecular markers for HPB cancers"""
    pathology_report = models.OneToOneField('PathologyReport', on_delete=models.CASCADE, related_name='molecular_markers')
    
    # KRAS status
    kras_mutation = models.BooleanField(default=False)
    kras_mutation_type = models.CharField(max_length=50, blank=True, choices=[
        ('G12D', 'G12D'),
        ('G12V', 'G12V'),
        ('G12R', 'G12R'),
        ('G12C', 'G12C'),
        ('G13D', 'G13D'),
        ('Q61H', 'Q61H'),
    ])
    
    # EGFR/HER2
    egfr_expression = models.CharField(max_length=20, blank=True, choices=[
        ('negative', 'Negative'),
        ('weak', 'Weak (1+)'),
        ('moderate', 'Moderate (2+)'),
        ('strong', 'Strong (3+)'),
    ])
    her2_status = models.CharField(max_length=20, blank=True, choices=[
        ('negative', 'Negative'),
        ('equivocal', 'Equivocal'),
        ('positive', 'Positive'),
    ])
    
    # MSI/Mismatch repair
    msi_status = models.CharField(max_length=20, blank=True, choices=[
        ('msi_h', 'MSI-High'),
        ('msi_l', 'MSI-Low'),
        ('mss', 'MSS (Microsatellite Stable)'),
    ])
    mlh1 = models.CharField(max_length=20, blank=True)
    msh2 = models.CharField(max_length=20, blank=True)
    msh6 = models.CharField(max_length=20, blank=True)
    pms2 = models.CharField(max_length=20, blank=True)
    
    # Other markers
    p53_status = models.CharField(max_length=20, blank=True, choices=[
        ('wildtype', 'Wildtype'),
        ('mutated', 'Mutated'),
        ('overexpressed', 'Overexpressed'),
    ])
    smad4_status = models.CharField(max_length=20, blank=True, choices=[
        ('intact', 'Intact'),
        ('lost', 'Lost'),
    ])
    
    # NGS findings
    ngs_performed = models.BooleanField(default=False)
    ngs_findings = models.TextField(blank=True, help_text="List all mutations found")
    
    # Additional comments
    comments = models.TextField(blank=True)
    
    def __str__(self):
        return f"Molecular markers for {self.pathology_report}"

class PathologyReport(models.Model):
    """Main pathology report for HPB specimens"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='pathology_reports')
    report_date = models.DateField()
    specimen_type = models.CharField(max_length=50, choices=[
        ('liver_resection', 'Liver Resection'),
        ('pancreatic_resection', 'Pancreatic Resection'),
        ('bile_duct_resection', 'Bile Duct Resection'),
        ('gallbladder', 'Gallbladder'),
        ('biopsy_liver', 'Liver Biopsy'),
        ('biopsy_pancreas', 'Pancreas Biopsy'),
        ('biopsy_lymph_node', 'Lymph Node Biopsy'),
        ('biopsy_peritoneal', 'Peritoneal Biopsy'),
    ])
    
    # Add these fields
    diagnosis = models.ForeignKey(
        Diagnosis, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='pathology_reports',
        help_text="ICD-10 diagnosis code"
    )
    
    histological_type = models.ForeignKey(
        HistologyType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pathology_reports',
        help_text="Histological type from standardized list"
    )
    
    diagnosis_notes = models.TextField(blank=True, help_text="Additional diagnostic notes if needed")
    histological_type_other = models.CharField(max_length=200, blank=True, help_text="If other histology type")
    
    # Tumor details
    tumor_size_cm = models.FloatField(validators=[MinValueValidator(0)], help_text="Largest tumor dimension in cm")
    tumor_size_other_dimensions = models.CharField(max_length=100, blank=True, help_text="e.g., 3.2 x 2.8 x 2.1 cm")
    number_of_tumors = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Tumor differentiation
    DIFFERENTIATION = [
        ('well', 'Well differentiated (Grade 1)'),
        ('moderate', 'Moderately differentiated (Grade 2)'),
        ('poor', 'Poorly differentiated (Grade 3)'),
        ('undifferentiated', 'Undifferentiated (Grade 4)'),
    ]
    differentiation = models.CharField(max_length=20, choices=DIFFERENTIATION, blank=True, null=True)
    
    # Margins
    margin_status = models.CharField(max_length=10, choices=[
        ('r0', 'R0 (Negative margin)'),
        ('r1', 'R1 (Microscopically positive)'),
        ('r2', 'R2 (Macroscopically positive)'),
        ('rx', 'RX (Margin cannot be assessed)'),
    ])
    margin_distance_mm = models.FloatField(null=True, blank=True, help_text="Distance from tumor to closest margin in mm")
    closest_margin = models.CharField(max_length=100, blank=True, help_text="e.g., Parenchymal, Bile duct, Vascular")
    
    # Vascular invasion
    microvascular_invasion = models.BooleanField(default=False)
    macrovascular_invasion = models.BooleanField(default=False)
    vascular_invasion_details = models.TextField(blank=True, help_text="Specify vessels involved")
    
    # Lymph nodes
    lymph_nodes_examined = models.IntegerField(default=0)
    lymph_nodes_positive = models.IntegerField(default=0)
    lymph_node_ratio = models.FloatField(null=True, blank=True, help_text="Positive/Examined ratio")
    lymph_node_stations = models.TextField(blank=True, help_text="Stations with positive nodes")
    
    # Perineural invasion
    perineural_invasion = models.BooleanField(default=False)
    
    # Peritoneal involvement
    peritoneal_invasion = models.BooleanField(default=False)
    
    # TNM Staging (AJCC 8th edition)
    t_stage = models.CharField(max_length=10, choices=[
        ('Tis', 'Tis - Carcinoma in situ'),
        ('T1', 'T1 - Tumor ≤2 cm'),
        ('T1a', 'T1a - Tumor ≤2 cm, single'),
        ('T1b', 'T1b - Tumor >2 cm, single'),
        ('T1c', 'T1c - Tumor >2 cm, single with vascular invasion'),
        ('T2', 'T2 - Multiple tumors, ≤5 cm'),
        ('T3', 'T3 - Multiple tumors, >5 cm or portal vein invasion'),
        ('T4', 'T4 - Tumor invades adjacent organs or perforates visceral peritoneum'),
    ], blank=True)
    
    n_stage = models.CharField(max_length=10, choices=[
        ('N0', 'N0 - No regional lymph node metastasis'),
        ('N1', 'N1 - Regional lymph node metastasis'),
    ], blank=True)
    
    m_stage = models.CharField(max_length=10, choices=[
        ('M0', 'M0 - No distant metastasis'),
        ('M1', 'M1 - Distant metastasis'),
    ], blank=True)
    
    # Liver-specific findings
    background_liver = models.TextField(blank=True, help_text="e.g., Cirrhosis, Steatosis, Hepatitis")
    fibrosis_score = models.IntegerField(null=True, blank=True, choices=[
        (0, 'F0 - No fibrosis'),
        (1, 'F1 - Portal fibrosis'),
        (2, 'F2 - Periportal fibrosis'),
        (3, 'F3 - Bridging fibrosis'),
        (4, 'F4 - Cirrhosis'),
    ])
    steatosis_percentage = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Pancreatic-specific findings
    pancreatic_parenchyma = models.TextField(blank=True, help_text="e.g., Chronic pancreatitis, IPMN, MCN")
    pancreatic_intraepithelial_neoplasia = models.CharField(max_length=50, blank=True, choices=[
        ('none', 'None'),
        ('panin_1', 'PanIN-1'),
        ('panin_2', 'PanIN-2'),
        ('panin_3', 'PanIN-3'),
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-report_date']
    
    def __str__(self):
        diag = self.diagnosis.diagnosis_name if self.diagnosis else "No diagnosis"
        return f"{self.patient} - {diag} ({self.report_date})"
    
    @property
    def lymph_node_ratio_calculated(self):
        """Calculate lymph node ratio"""
        if self.lymph_nodes_examined > 0:
            return round(self.lymph_nodes_positive / self.lymph_nodes_examined, 2)
        return None
