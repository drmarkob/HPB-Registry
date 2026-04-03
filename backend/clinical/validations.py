from django.core.exceptions import ValidationError
from datetime import date

def validate_surgical_procedure(instance):
    """Validate SurgicalProcedure model"""
    errors = {}
    
    if instance.procedure_date and instance.procedure_date > date.today():
        errors['procedure_date'] = 'Procedure date cannot be in the future'
    
    if instance.procedure_date and instance.patient.date_of_birth:
        if instance.procedure_date < instance.patient.date_of_birth:
            errors['procedure_date'] = 'Procedure date cannot be before patient birth date'
    
    if instance.operative_time_minutes and instance.operative_time_minutes < 0:
        errors['operative_time_minutes'] = 'Operative time cannot be negative'
    if instance.operative_time_minutes and instance.operative_time_minutes > 720:
        errors['operative_time_minutes'] = 'Operative time seems too high (>12 hours)'
    
    if instance.blood_loss_ml and instance.blood_loss_ml < 0:
        errors['blood_loss_ml'] = 'Blood loss cannot be negative'
    if instance.blood_loss_ml and instance.blood_loss_ml > 20000:
        errors['blood_loss_ml'] = 'Blood loss seems too high (>20L)'
    
    if instance.pringle_maneuver:
        if not instance.pringle_time_minutes:
            errors['pringle_time_minutes'] = 'Pringle time required when maneuver used'
    else:
        if instance.pringle_time_minutes:
            errors['pringle_maneuver'] = 'Pringle maneuver must be True if time provided'
    
    if errors:
        raise ValidationError(errors)

def validate_follow_up(instance):
    """Validate FollowUp model"""
    errors = {}
    
    if instance.followup_date and instance.followup_date > date.today():
        errors['followup_date'] = 'Follow-up date cannot be in the future'
    
    if not instance.alive and not instance.date_of_death:
        errors['date_of_death'] = 'Date of death required when patient is deceased'
    
    if instance.date_of_death and instance.alive:
        errors['alive'] = 'Patient cannot be alive with death date provided'
    
    if instance.recurrence and not instance.recurrence_date:
        errors['recurrence_date'] = 'Recurrence date required when recurrence is True'
    
    if instance.recurrence_date and not instance.recurrence:
        errors['recurrence'] = 'Recurrence must be True if recurrence date provided'
    
    if instance.date_of_death and instance.recurrence_date:
        if instance.recurrence_date > instance.date_of_death:
            errors['recurrence_date'] = 'Recurrence date cannot be after death date'
    
    if errors:
        raise ValidationError(errors)
