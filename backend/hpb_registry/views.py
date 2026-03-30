from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from patients.models import Patient
from clinical.models import SurgicalProcedure
from pathology.models import PathologyReport

@staff_member_required
def custom_dashboard(request):
    context = {
        'total_patients': Patient.objects.count(),
        'total_surgeries': SurgicalProcedure.objects.count(),
        'total_pathology': PathologyReport.objects.count(),
        'recent_patients': Patient.objects.order_by('-created_at')[:5],
    }
    return render(request, 'admin/custom_dashboard.html', context)
