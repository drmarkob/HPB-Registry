from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from patients.models import Patient

class LiverResectionDetail(models.Model):
    """Detailed liver resection data"""
    surgical_procedure = models.OneToOneField('SurgicalProcedure', on_delete=models.CASCADE, related_name='liver_details')
    
    # Liver resection type
    RESECTION_TYPES = [
        ('anatomical', 'Anatomical Resection'),
        ('non_anatomical', 'Non-anatomical (Wedge)'),
        ('combined', 'Combined Anatomical + Non-anatomical'),
    ]
    resection_type = models.CharField(max_length=20, choices=RESECTION_TYPES, default='anatomical')
    
    # Segments resected (Couinaud classification)
    segment_1 = models.BooleanField(default=False, help_text="Caudate lobe")
    segment_2 = models.BooleanField(default=False)
    segment_3 = models.BooleanField(default=False)
    segment_4a = models.BooleanField(default=False)
    segment_4b = models.BooleanField(default=False)
    segment_5 = models.BooleanField(default=False)
    segment_6 = models.BooleanField(default=False)
    segment_7 = models.BooleanField(default=False)
    segment_8 = models.BooleanField(default=False)
    
    # Resection extent
    HEPATECTOMY_TYPES = [
        ('less_than_section', 'Less than one section'),
        ('left_lateral_sectionectomy', 'Left lateral sectionectomy (Segments 2-3)'),
        ('left_hepatectomy', 'Left hepatectomy (Segments 2-4)'),
        ('right_posterior_sectionectomy', 'Right posterior sectionectomy (Segments 6-7)'),
        ('right_anterior_sectionectomy', 'Right anterior sectionectomy (Segments 5-8)'),
        ('right_hepatectomy', 'Right hepatectomy (Segments 5-8)'),
        ('extended_left_hepatectomy', 'Extended left hepatectomy (Segments 2-5,8)'),
        ('extended_right_hepatectomy', 'Extended right hepatectomy (Segments 4-8)'),
        ('central_hepatectomy', 'Central hepatectomy (Segments 4,5,8)'),
        ('trisegmentectomy', 'Trisegmentectomy'),
    ]
    hepatectomy_type = models.CharField(max_length=50, choices=HEPATECTOMY_TYPES, default='less_than_section')
    
    # Number of segments resected
    number_of_segments = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(8)], 
                                             null=True, blank=True,
                                             help_text="Total number of Couinaud segments resected")
    
    # Tumor details
    total_tumor_count = models.IntegerField(default=0, help_text="Auto-calculated from individual tumors")
    largest_tumor_size_cm = models.FloatField(null=True, blank=True, help_text="Auto-calculated from individual tumors")
    total_tumor_volume_cc = models.FloatField(null=True, blank=True, help_text="Auto-calculated from individual tumors")
    
    # Margins
    margin_status = models.CharField(max_length=20, 
                                     choices=[('r0', 'R0 (Negative margin)'),
                                             ('r1', 'R1 (Microscopically positive)'),
                                             ('r2', 'R2 (Macroscopically positive)')],
                                     null=True, blank=True)
    margin_distance_mm = models.FloatField(null=True, blank=True, help_text="Distance from tumor to resection margin in mm")
    
    # Parenchymal quality
    LIVER_PARENCHYMA = [
        ('normal', 'Normal'),
        ('steatosis_mild', 'Steatosis <30%'),
        ('steatosis_moderate', 'Steatosis 30-60%'),
        ('steatosis_severe', 'Steatosis >60%'),
        ('cirrhosis_compensated', 'Cirrhosis - Child-Pugh A'),
        ('cirrhosis_decompensated', 'Cirrhosis - Child-Pugh B/C'),
        ('fibrosis', 'Fibrosis without cirrhosis'),
    ]
    parenchyma_quality = models.CharField(max_length=50, choices=LIVER_PARENCHYMA, default='normal')
    
    # Future liver remnant
    flr_percentage = models.FloatField(null=True, blank=True, help_text="Future liver remnant percentage")
    flr_volume_cc = models.FloatField(null=True, blank=True, help_text="Future liver remnant volume in cc")
    
    # Vascular reconstruction
    portal_vein_reconstruction = models.BooleanField(default=False)
    hepatic_artery_reconstruction = models.BooleanField(default=False)
    hepatic_vein_reconstruction = models.BooleanField(default=False)
    ivc_resection = models.BooleanField(default=False)
    
    def update_tumor_stats(self):
        """Update aggregated statistics from individual tumors"""
        tumors = self.tumors.all()
        self.total_tumor_count = tumors.count()
        if tumors.exists():
            self.largest_tumor_size_cm = max(t.size_cm for t in tumors)
        self.save()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_tumor_stats()

    def __str__(self):
        return f"Liver resection: {self.get_hepatectomy_type_display()} - {self.surgical_procedure.patient}"

class PancreaticResectionDetail(models.Model):
    """Detailed pancreatic surgery data"""
    surgical_procedure = models.OneToOneField('SurgicalProcedure', on_delete=models.CASCADE, related_name='pancreatic_details')
    
    # Pancreatic resection type specifics
    PANCREATECTOMY_VARIANTS = [
        ('standard_whipple', 'Standard Whipple (Pancreaticoduodenectomy)'),
        ('pylorus_preserving', 'Pylorus-preserving Pancreaticoduodenectomy (PPPD)'),
        ('distal_pancreatectomy', 'Distal Pancreatectomy'),
        ('central_pancreatectomy', 'Central Pancreatectomy'),
        ('total_pancreatectomy', 'Total Pancreatectomy'),
        ('enucleation', 'Enucleation'),
    ]
    pancreatectomy_variant = models.CharField(max_length=50, choices=PANCREATECTOMY_VARIANTS, default='standard_whipple')
    
    # Tumor location
    TUMOR_LOCATION = [
        ('head', 'Pancreatic Head'),
        ('uncinate', 'Uncinate Process'),
        ('neck', 'Pancreatic Neck'),
        ('body', 'Pancreatic Body'),
        ('tail', 'Pancreatic Tail'),
        ('diffuse', 'Diffuse/Multiple'),
    ]
    tumor_location = models.CharField(max_length=20, choices=TUMOR_LOCATION, default='head')
    
    # Tumor size
    tumor_size_cm = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)
    
    # Pancreatic duct
    pancreatic_duct_dilated = models.BooleanField(default=False)
    pancreatic_duct_size_mm = models.FloatField(null=True, blank=True)
    pancreatic_duct_stent = models.BooleanField(default=False)
    
    # Vascular involvement
    portal_vein_invasion = models.BooleanField(default=False)
    portal_vein_resection = models.BooleanField(default=False)
    portal_vein_reconstruction_type = models.CharField(max_length=50, blank=True,
                                                       choices=[('primary_repair', 'Primary Repair'),
                                                               ('patch', 'Patch Repair'),
                                                               ('interposition_graft', 'Interposition Graft'),
                                                               ('vein_graft', 'Vein Graft')])
    
    superior_mesenteric_vein_invasion = models.BooleanField(default=False)
    superior_mesenteric_artery_invasion = models.BooleanField(default=False)
    celiac_axis_invasion = models.BooleanField(default=False)
    hepatic_artery_invasion = models.BooleanField(default=False)
    
    # Pancreatic texture
    PANCREATIC_TEXTURE = [
        ('soft', 'Soft'),
        ('intermediate', 'Intermediate'),
        ('hard', 'Hard (Fibrotic)'),
    ]
    pancreatic_texture = models.CharField(max_length=20, choices=PANCREATIC_TEXTURE, default='soft')
    
    # Pancreatic anastomosis
    ANASTOMOSIS_TYPE = [
        ('duct_to_mucosa', 'Duct-to-mucosa'),
        ('invagination', 'Invagination (Dunking)'),
        ('binding', 'Binding Pancreaticojejunostomy'),
        ('blumgart', 'Blumgart Anastomosis'),
    ]
    anastomosis_type = models.CharField(max_length=20, choices=ANASTOMOSIS_TYPE, default='duct_to_mucosa')
    pancreatic_jejunostomy = models.BooleanField(default=True)
    pancreatic_gastrostomy = models.BooleanField(default=False)
    
    # Drain
    external_drain_placed = models.BooleanField(default=True)
    drain_amylase_pod1 = models.FloatField(null=True, blank=True, help_text="Drain amylase on POD 1 (U/L)")
    drain_amylase_pod3 = models.FloatField(null=True, blank=True, help_text="Drain amylase on POD 3 (U/L)")
    drain_removal_day = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"Pancreatic resection: {self.get_pancreatectomy_variant_display()} - {self.surgical_procedure.patient}"

class BiliaryProcedureDetail(models.Model):
    """Detailed biliary surgery data"""
    surgical_procedure = models.OneToOneField('SurgicalProcedure', on_delete=models.CASCADE, related_name='biliary_details')
    
    # Biliary procedure type
    BILIARY_PROCEDURES = [
        ('cholecystectomy', 'Cholecystectomy'),
        ('bile_duct_exploration', 'Bile Duct Exploration'),
        ('choledochojejunostomy', 'Choledochojejunostomy'),
        ('hepaticojejunostomy', 'Hepaticojejunostomy'),
        ('bile_duct_resection', 'Bile Duct Resection'),
        ('hilar_resection', 'Hilar Resection (Klatskin)'),
        ('transhepatic_drain', 'Transhepatic Drain Placement'),
    ]
    biliary_procedure = models.CharField(max_length=50, choices=BILIARY_PROCEDURES)
    
    # Bile duct level (for hilar tumors)
    BISMUTH_CLASSIFICATION = [
        ('type1', 'Type I - Below confluence'),
        ('type2', 'Type II - At confluence'),
        ('type3a', 'Type IIIa - Extends to right hepatic duct'),
        ('type3b', 'Type IIIb - Extends to left hepatic duct'),
        ('type4', 'Type IV - Multifocal/involving both sides'),
    ]
    bismuth_classification = models.CharField(max_length=10, choices=BISMUTH_CLASSIFICATION, null=True, blank=True)
    
    # Bile duct details
    bile_duct_diameter_mm = models.FloatField(null=True, blank=True)
    bile_duct_stricture = models.BooleanField(default=False)
    stricture_location = models.CharField(max_length=100, blank=True)
    
    # Anastomosis details
    anastomosis_level = models.CharField(max_length=50, blank=True,
                                         choices=[('infrahilar', 'Infrahilar'),
                                                 ('hilar', 'Hilar'),
                                                 ('suprahilar', 'Suprahilar'),
                                                 ('intrahepatic', 'Intrahepatic')])
    number_of_anastomoses = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Stents
    preoperative_stent = models.BooleanField(default=False)
    preoperative_stent_type = models.CharField(max_length=50, blank=True,
                                              choices=[('plastic', 'Plastic Stent'),
                                                      ('metal', 'Metal Stent'),
                                                      ('both', 'Both')])
    postoperative_stent = models.BooleanField(default=False)
    
    # Bile leak management
    bile_leak_management = models.TextField(blank=True, help_text="How was bile leak managed?")
    ercp_performed = models.BooleanField(default=False)
    ptbd_performed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Biliary procedure: {self.get_biliary_procedure_display()} - {self.surgical_procedure.patient}"

class SurgicalProcedure(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='surgeries')
    procedure_date = models.DateField()
    
    # Procedure type
    PROCEDURE_TYPES = [
        ('liver_surgery', 'Liver Surgery'),
        ('pancreatic_surgery', 'Pancreatic Surgery'),
        ('biliary_surgery', 'Biliary Surgery'),
        ('combined', 'Combined Procedure'),
    ]
    
    procedure_type = models.CharField(max_length=50, choices=PROCEDURE_TYPES, default='liver_surgery')
    
    # Subtype
    liver_surgery_subtype = models.CharField(
        max_length=50, blank=True, default='',
        choices=[
            ('hepatectomy_major', 'Major Hepatectomy (≥3 segments)'),
            ('hepatectomy_minor', 'Minor Hepatectomy (<3 segments)'),
            ('non_anatomical', 'Non-anatomical Resection'),
            ('ablative', 'Ablative Procedure'),
            ('fenestration', 'Fenestration (for cysts)'),
            ('deroofing', 'Deroofing'),
            ('biopsy', 'Liver Biopsy'),
            ('liver_transplant', 'Liver Transplantation'),
        ],
        verbose_name="Liver Surgery Subtype"
    )
    
    pancreatic_surgery_subtype = models.CharField(
        max_length=50, blank=True, default='',
        choices=[
            ('whipple', 'Whipple Procedure (Pancreaticoduodenectomy)'),
            ('distal', 'Distal Pancreatectomy'),
            ('central', 'Central Pancreatectomy'),
            ('total', 'Total Pancreatectomy'),
            ('enucleation', 'Enucleation'),
            ('drainage', 'Drainage Procedure (Puestow, Frey)'),
            ('necrosectomy', 'Necrosectomy'),
            ('cystogastrostomy', 'Cystogastrostomy'),
            ('biopsy', 'Pancreatic Biopsy'),
        ],
        verbose_name="Pancreatic Surgery Subtype"
    )
    
    biliary_surgery_subtype = models.CharField(
        max_length=50, blank=True, default='',
        choices=[
            ('cholecystectomy', 'Cholecystectomy'),
            ('bd_resection', 'Bile Duct Resection'),
            ('bypass', 'Biliary Bypass'),
            ('hepaticojejunostomy', 'Hepaticojejunostomy'),
            ('choledochojejunostomy', 'Choledochojejunostomy'),
            ('stent_placement', 'Stent Placement'),
            ('ptbd', 'PTBD - Percutaneous Transhepatic Biliary Drainage'),
            ('ercp', 'ERCP'),
        ],
        verbose_name="Biliary Surgery Subtype"
    )
    
    # Surgical approach
    APPROACH_CHOICES = [
        ('open', 'Open'),
        ('laparoscopic', 'Laparoscopic'),
        ('robotic', 'Robotic'),
        ('converted', 'Converted (Laparoscopic to Open)'),
    ]
    surgical_approach = models.CharField(max_length=20, choices=APPROACH_CHOICES, default='open')

    # Operative details
    operative_time_minutes = models.IntegerField(validators=[MinValueValidator(0)])
    blood_loss_ml = models.IntegerField(validators=[MinValueValidator(0)])
    intraoperative_transfusion = models.BooleanField(default=False)
    transfusion_units = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Pringle maneuver
    pringle_maneuver = models.BooleanField(default=False)
    pringle_time_minutes = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    pringle_cycles = models.IntegerField(null=True, blank=True, default=None, validators=[MinValueValidator(0)])
    
    CLAVIEN_DINDO_CHOICES = [
        (0, 'No complication'),
        (1, 'Grade I - Any deviation from normal course'),
        (2, 'Grade II - Pharmacologic treatment'),
        (3, 'Grade IIIa - Intervention without general anesthesia'),
        (4, 'Grade IIIb - Intervention with general anesthesia'),
        (5, 'Grade IVa - Single organ dysfunction'),
        (6, 'Grade IVb - Multiorgan dysfunction'),
        (7, 'Grade V - Death'),
    ]

    # Complications
    clavien_dindo_grade = models.IntegerField(choices=CLAVIEN_DINDO_CHOICES, blank=True, null=True)
    
    # Postoperative stay
    hospital_stay_days = models.IntegerField(null=True, blank=True)
    icu_stay_days = models.IntegerField(null=True, blank=True)
    
    # Readmission
    readmission_30d = models.BooleanField(default=False)
    readmission_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-procedure_date']
    
    def __str__(self):
        return f"{self.get_procedure_type_display()} - {self.patient} - {self.procedure_date}"

class ChemotherapyProtocol(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='chemotherapy')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    PROTOCOLS = [
        ('folfox', 'FOLFOX (Oxaliplatin, 5-FU, Leucovorin)'),
        ('folfiri', 'FOLFIRI (Irinotecan, 5-FU, Leucovorin)'),
        ('gemcitabine', 'Gemcitabine monotherapy'),
        ('gemcitabine_capecitabine', 'Gemcitabine + Capecitabine'),
        ('folfirinox', 'FOLFIRINOX (5-FU, Leucovorin, Irinotecan, Oxaliplatin)'),
        ('capecitabine', 'Capecitabine monotherapy'),
        ('sorafenib', 'Sorafenib'),
        ('other', 'Other protocol'),
    ]
    
    protocol = models.CharField(max_length=50, choices=PROTOCOLS)
    other_protocol_name = models.CharField(max_length=100, blank=True, help_text="If other protocol selected")
    cycles_planned = models.IntegerField()
    cycles_completed = models.IntegerField()
    
    # Chemotherapy setting
    SETTING_CHOICES = [
        ('neoadjuvant', 'Neoadjuvant (preoperative)'),
        ('adjuvant', 'Adjuvant (postoperative)'),
        ('palliative', 'Palliative'),
        ('conversion', 'Conversion therapy'),
    ]
    setting = models.CharField(max_length=20, choices=SETTING_CHOICES)
    
    # Toxicity (CTCAE grading)
    neurotoxicity_grade = models.IntegerField(choices=[(0, 'None'), (1, 'Mild'), (2, 'Moderate'), (3, 'Severe'), (4, 'Life-threatening')], default=0)
    neutropenia_grade = models.IntegerField(choices=[(0, 'None'), (1, 'Mild'), (2, 'Moderate'), (3, 'Severe'), (4, 'Life-threatening')], default=0)
    thrombocytopenia_grade = models.IntegerField(choices=[(0, 'None'), (1, 'Mild'), (2, 'Moderate'), (3, 'Severe'), (4, 'Life-threatening')], default=0)
    
    dose_reduction = models.BooleanField(default=False)
    dose_reduction_reason = models.TextField(blank=True)
    treatment_delayed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = "Chemotherapy protocols"
    
    def __str__(self):
        return f"{self.get_protocol_display()} - {self.patient}"

class FollowUp(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='followups')
    followup_date = models.DateField()
    
    # Survival
    alive = models.BooleanField(default=True)
    date_of_death = models.DateField(null=True, blank=True)
    cause_of_death = models.TextField(blank=True)
    
    # Recurrence
    recurrence = models.BooleanField(default=False)
    recurrence_date = models.DateField(null=True, blank=True)
    RECURRENCE_TYPES = [
        ('local', 'Local recurrence'),
        ('distant', 'Distant metastasis'),
        ('both', 'Local and distant'),
    ]
    recurrence_type = models.CharField(max_length=20, choices=RECURRENCE_TYPES, blank=True)
    recurrence_site = models.TextField(blank=True, help_text="Specify location of recurrence/metastasis")
    
    # Quality of life
    ECOG_CHOICES = [
        (0, 'Fully active, able to carry on all pre-disease performance without restriction'),
        (1, 'Restricted in physically strenuous activity but ambulatory and able to carry out work'),
        (2, 'Ambulatory and capable of all self-care but unable to carry out any work activities'),
        (3, 'Capable of only limited self-care, confined to bed or chair >50% of waking hours'),
        (4, 'Completely disabled, cannot carry on any self-care, totally confined to bed or chair'),
    ]
    ecog_status = models.IntegerField(choices=ECOG_CHOICES, blank=True, null=True)
    
    # Tumor markers
    ca19_9 = models.FloatField(null=True, blank=True, help_text="U/mL")
    cea = models.FloatField(null=True, blank=True, help_text="ng/mL")
    afp = models.FloatField(null=True, blank=True, help_text="ng/mL")
    
    # Treatment after recurrence
    salvage_surgery = models.BooleanField(default=False)
    salvage_chemotherapy = models.BooleanField(default=False)
    salvage_radiotherapy = models.BooleanField(default=False)
    
    # Comments
    clinical_notes = models.TextField(blank=True)

    disease_free_survival_months = models.FloatField(
        null=True, blank=True, 
        help_text="Months until recurrence or death"
    )
    overall_survival_months = models.FloatField(
        null=True, blank=True, 
        help_text="Months from surgery to death or last follow-up"
    )
    recurrence_free_survival_months = models.FloatField(
        null=True, blank=True, 
        help_text="Months from surgery to recurrence"
    )
    last_known_alive_date = models.DateField(
        null=True, blank=True, 
        help_text="Date patient was last confirmed alive"
    )
    
    class Meta:
        ordering = ['-followup_date']
        verbose_name_plural = "Follow-ups"
    
    def __str__(self):
        return f"Follow-up {self.followup_date} - {self.patient}"
    
    @property
    def survival_months(self):
        if self.date_of_death:
            delta = self.date_of_death - self.followup_date
            return round(delta.days / 30.44, 1)
        return None

class LiverTumor(models.Model):
    """Individual liver tumor details for precise mapping"""
    liver_resection = models.ForeignKey(
        'LiverResectionDetail', 
        on_delete=models.CASCADE, 
        related_name='tumors'
    )
    
    # Tumor location by Couinaud segment
    SEGMENT_CHOICES = [
        ('S1', 'Segment I - Caudate lobe'),
        ('S2', 'Segment II'),
        ('S3', 'Segment III'),
        ('S4a', 'Segment IVa'),
        ('S4b', 'Segment IVb'),
        ('S5', 'Segment V'),
        ('S6', 'Segment VI'),
        ('S7', 'Segment VII'),
        ('S8', 'Segment VIII'),
        ('multiple', 'Multiple segments involved'),
    ]
    
    segment = models.CharField(max_length=10, choices=SEGMENT_CHOICES, help_text="Couinaud segment")
    segment_details = models.CharField(max_length=100, blank=True, help_text="If multiple segments, specify")
    
    # Tumor dimensions
    size_cm = models.FloatField(validators=[MinValueValidator(0)], help_text="Largest dimension in cm")
    size_other_dimensions = models.CharField(max_length=50, blank=True, help_text="e.g., 3.2 x 2.8 x 2.1 cm")
    
    # Tumor characteristics
    is_primary = models.BooleanField(default=True, help_text="Primary tumor vs metastasis")
    
    DIFFERENTIATION_CHOICES = [
        ('well', 'Well differentiated (Grade 1)'),
        ('moderate', 'Moderately differentiated (Grade 2)'),
        ('poor', 'Poorly differentiated (Grade 3)'),
        ('undifferentiated', 'Undifferentiated (Grade 4)'),
        ('unknown', 'Unknown'),
    ]
    differentiation = models.CharField(max_length=20, choices=DIFFERENTIATION_CHOICES, blank=True)
    
    # Vascular invasion for this specific tumor
    microvascular_invasion = models.BooleanField(default=False)
    macrovascular_invasion = models.BooleanField(default=False)
    
    # Necrosis
    necrosis_percentage = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of tumor necrosis (after neoadjuvant therapy)"
    )
    
    # Additional notes
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['segment']
    
    def __str__(self):
        return f"Tumor in {self.segment}: {self.size_cm} cm"

class TextbookOutcome(models.Model):
    """Textbook outcome quality metric for surgical procedures"""
    surgical_procedure = models.OneToOneField(
        'SurgicalProcedure', 
        on_delete=models.CASCADE, 
        related_name='textbook_outcome'
    )
    
    # Textbook outcome components
    no_major_complications = models.BooleanField(
        default=False, 
        help_text="No Clavien-Dindo ≥ III complications"
    )
    no_prolonged_los = models.BooleanField(
        default=False, 
        help_text="Length of stay ≤ 75th percentile for procedure"
    )
    no_readmission = models.BooleanField(
        default=False, 
        help_text="No 30-day readmission"
    )
    no_mortality = models.BooleanField(
        default=False, 
        help_text="No 30-day mortality"
    )
    negative_margins = models.BooleanField(
        default=False, 
        help_text="R0 resection"
    )
    adequate_lymph_node_yield = models.BooleanField(
        default=False, 
        help_text="≥12 lymph nodes examined"
    )
    
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Textbook Outcome"
        verbose_name_plural = "Textbook Outcomes"
    
    @property
    def achieved(self):
        """Check if textbook outcome was achieved"""
        return all([
            self.no_major_complications,
            self.no_prolonged_los,
            self.no_readmission,
            self.no_mortality,
            self.negative_margins,
            self.adequate_lymph_node_yield
        ])
    
    def __str__(self):
        return f"Textbook Outcome: {'Achieved' if self.achieved else 'Not Achieved'}"
