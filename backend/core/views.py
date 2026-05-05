from django.shortcuts import render
from .models import ContratoAuditado

def dashboard(request):
    contratos = ContratoAuditado.objects.all().order_by('-fecha_subida')
    return render(request, 'dashboard.html', {'contratos': contratos})