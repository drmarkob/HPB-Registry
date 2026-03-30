from django.db import migrations
from django.db.models import Q

def migrate_popf_data(apps, schema_editor):
    """Migrate existing POPF data from SurgicalProcedure to PancreaticComplication"""
    SurgicalProcedure = apps.get_model('clinical', 'SurgicalProcedure')
    PancreaticComplication = apps.get_model('complications', 'PancreaticComplication')
    
    for surgery in SurgicalProcedure.objects.filter(popf_present=True):
        if surgery.popf_grade in ['B', 'C']:
            complication_type = 'popf_grade_b' if surgery.popf_grade == 'B' else 'popf_grade_c'
            PancreaticComplication.objects.create(
                surgical_procedure=surgery,
                complication_type=complication_type,
                onset_days=3,  # Default, adjust as needed
                clavien_grade=3 if surgery.popf_grade == 'B' else 4,
                popf_drain_amylase=surgery.popf_drain_amylase,
                drain_amylase_pod1=surgery.popf_drain_amylase,
                resolved=True,
                treatment="Conservative management" if surgery.popf_grade == 'B' else "Intervention required"
            )

def migrate_bile_leak_data(apps, schema_editor):
    """Migrate existing Bile Leak data from SurgicalProcedure to GeneralComplication"""
    SurgicalProcedure = apps.get_model('clinical', 'SurgicalProcedure')
    GeneralComplication = apps.get_model('complications', 'GeneralComplication')
    
    for surgery in SurgicalProcedure.objects.filter(bile_leak=True):
        if surgery.bile_leak_grade:
            complication_type = f'bile_leak_grade_{surgery.bile_leak_grade.lower()}'
            GeneralComplication.objects.create(
                surgical_procedure=surgery,
                complication_type=complication_type,
                onset_days=5,  # Default, adjust as needed
                clavien_grade=2 if surgery.bile_leak_grade == 'A' else 3,
                intervention_required=surgery.bile_leak_grade in ['B', 'C'],
                intervention_type=surgery.bile_leak_treatment[:100] if surgery.bile_leak_treatment else '',
                treatment=surgery.bile_leak_treatment,
                resolved=True
            )

class Migration(migrations.Migration):
    dependencies = [
        ('complications', '0001_initial'),
        ('clinical', '0005_remove_liverresectiondetail_number_of_tumors_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_popf_data),
        migrations.RunPython(migrate_bile_leak_data),
    ]
