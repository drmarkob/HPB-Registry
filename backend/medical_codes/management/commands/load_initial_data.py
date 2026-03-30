from django.core.management.base import BaseCommand
from medical_codes.models import Diagnosis, HistologyType

class Command(BaseCommand):
    help = 'Load initial diagnoses and histology types for HPB surgery'

    def handle(self, *args, **options):
        
        # Load Diagnoses with ICD-10 codes
        diagnoses = [
            # Liver - Malignant
            ('C22.0', 'Hepatocellular carcinoma (HCC)', 'liver_malignant'),
            ('C22.1', 'Intrahepatic cholangiocarcinoma (ICC)', 'liver_malignant'),
            ('C22.2', 'Hepatoblastoma', 'liver_malignant'),
            ('C22.3', 'Angiosarcoma of liver', 'liver_malignant'),
            ('C22.7', 'Other malignant neoplasms of liver', 'liver_malignant'),
            ('C22.9', 'Malignant neoplasm of liver, unspecified', 'liver_malignant'),
            
            # Liver - Benign
            ('D13.4', 'Benign neoplasm of liver', 'liver_benign'),
            ('D18.0', 'Hemangioma of liver', 'liver_benign'),
            ('K76.0', 'Fatty liver (steatosis)', 'liver_benign'),
            ('K74.0', 'Hepatic fibrosis', 'liver_benign'),
            ('K74.6', 'Cirrhosis of liver', 'liver_benign'),
            ('K75.8', 'Focal nodular hyperplasia (FNH)', 'liver_benign'),
            
            # Pancreas - Malignant
            ('C25.0', 'Pancreatic adenocarcinoma - Head', 'pancreas_malignant'),
            ('C25.1', 'Pancreatic adenocarcinoma - Body', 'pancreas_malignant'),
            ('C25.2', 'Pancreatic adenocarcinoma - Tail', 'pancreas_malignant'),
            ('C25.3', 'Pancreatic ductal adenocarcinoma (PDAC)', 'pancreas_malignant'),
            ('C25.4', 'Pancreatic neuroendocrine tumor (PNET)', 'pancreas_malignant'),
            ('C25.7', 'Malignant neoplasm of other parts of pancreas', 'pancreas_malignant'),
            ('C25.9', 'Malignant neoplasm of pancreas, unspecified', 'pancreas_malignant'),
            
            # Pancreas - Benign
            ('D13.6', 'Benign neoplasm of pancreas', 'pancreas_benign'),
            ('D13.7', 'Benign neoplasm of pancreatic duct', 'pancreas_benign'),
            ('K86.1', 'Chronic pancreatitis', 'pancreas_benign'),
            ('K86.2', 'Pancreatic cyst', 'pancreas_benign'),
            ('K86.8', 'Other specified diseases of pancreas', 'pancreas_benign'),
            ('M8140', 'Serous cystadenoma', 'pancreas_benign'),
            ('M8470', 'Mucinous cystadenoma', 'pancreas_benign'),
            ('M8453', 'Intraductal papillary mucinous neoplasm (IPMN)', 'pancreas_benign'),
            
            # Biliary - Malignant
            ('C23', 'Gallbladder carcinoma', 'biliary_malignant'),
            ('C24.0', 'Extrahepatic bile duct carcinoma', 'biliary_malignant'),
            ('C24.1', 'Ampulla of Vater carcinoma', 'biliary_malignant'),
            ('C24.8', 'Overlapping malignant lesion of biliary tract', 'biliary_malignant'),
            ('C24.9', 'Malignant neoplasm of biliary tract, unspecified', 'biliary_malignant'),
            
            # Biliary - Benign
            ('D13.5', 'Benign neoplasm of extrahepatic bile ducts', 'biliary_benign'),
            ('K80.0', 'Cholelithiasis with cholecystitis', 'biliary_benign'),
            ('K80.1', 'Cholelithiasis with other cholecystitis', 'biliary_benign'),
            ('K80.2', 'Cholelithiasis without cholecystitis', 'biliary_benign'),
            ('K81.0', 'Acute cholecystitis', 'biliary_benign'),
            ('K81.1', 'Chronic cholecystitis', 'biliary_benign'),
            ('K82.0', 'Gallbladder polyp', 'biliary_benign'),
            ('K83.0', 'Cholangitis', 'biliary_benign'),
            ('K83.1', 'Bile duct obstruction', 'biliary_benign'),
        ]
        
        for code, name, category in diagnoses:
            obj, created = Diagnosis.objects.get_or_create(
                icd10_code=code,
                defaults={
                    'diagnosis_name': name,
                    'category': category
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created diagnosis: {code} - {name}'))
        
        # Load Histology Types
        histologies = [
            # Malignant
            ('Hepatocellular carcinoma', 'malignant', 'liver'),
            ('Cholangiocarcinoma', 'malignant', 'biliary'),
            ('Combined hepatocellular-cholangiocarcinoma', 'malignant', 'liver'),
            ('Pancreatic ductal adenocarcinoma', 'malignant', 'pancreas'),
            ('Acinar cell carcinoma', 'malignant', 'pancreas'),
            ('Neuroendocrine tumor - Grade 1', 'malignant', 'general'),
            ('Neuroendocrine tumor - Grade 2', 'malignant', 'general'),
            ('Neuroendocrine tumor - Grade 3', 'malignant', 'general'),
            ('Small cell carcinoma', 'malignant', 'general'),
            ('Squamous cell carcinoma', 'malignant', 'general'),
            ('Adenosquamous carcinoma', 'malignant', 'general'),
            ('Undifferentiated carcinoma', 'malignant', 'general'),
            ('Sarcomatoid carcinoma', 'malignant', 'general'),
            ('Angiosarcoma', 'malignant', 'liver'),
            ('Leiomyosarcoma', 'malignant', 'general'),
            ('Lymphoma', 'malignant', 'general'),
            ('Metastatic carcinoma', 'malignant', 'general'),
            
            # Premalignant
            ('Intraductal papillary mucinous neoplasm (IPMN) - Low grade', 'premalignant', 'pancreas'),
            ('Intraductal papillary mucinous neoplasm (IPMN) - High grade', 'premalignant', 'pancreas'),
            ('Mucinous cystic neoplasm (MCN) - Low grade', 'premalignant', 'pancreas'),
            ('Mucinous cystic neoplasm (MCN) - High grade', 'premalignant', 'pancreas'),
            ('Pancreatic intraepithelial neoplasia (PanIN)-1', 'premalignant', 'pancreas'),
            ('Pancreatic intraepithelial neoplasia (PanIN)-2', 'premalignant', 'pancreas'),
            ('Pancreatic intraepithelial neoplasia (PanIN)-3', 'premalignant', 'pancreas'),
            ('Biliary intraepithelial neoplasia (BilIN)', 'premalignant', 'biliary'),
            ('Dysplasia in gallbladder', 'premalignant', 'biliary'),
            ('Dysplasia in bile duct', 'premalignant', 'biliary'),
            
            # Benign
            ('Hepatocellular adenoma', 'benign', 'liver'),
            ('Focal nodular hyperplasia', 'benign', 'liver'),
            ('Hemangioma', 'benign', 'liver'),
            ('Simple cyst', 'benign', 'general'),
            ('Polycystic liver disease', 'benign', 'liver'),
            ('Serous cystadenoma', 'benign', 'pancreas'),
            ('Mucinous cystadenoma', 'benign', 'pancreas'),
            ('Solid pseudopapillary neoplasm', 'benign', 'pancreas'),
            ('Pancreatic pseudocyst', 'benign', 'pancreas'),
            ('Adenomyomatosis of gallbladder', 'benign', 'biliary'),
            ('Cholesterol polyp', 'benign', 'biliary'),
            ('Gallbladder polyp', 'benign', 'biliary'),
            ('Inflammatory polyp', 'benign', 'general'),
            ('Granulomatous inflammation', 'benign', 'general'),
            ('Normal tissue', 'benign', 'general'),
        ]
        
        for name, category, organ in histologies:
            obj, created = HistologyType.objects.get_or_create(
                name=name,
                defaults={
                    'category': category,
                    'organ_system': organ
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created histology: {name}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded all medical data!'))
