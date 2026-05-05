from django.shortcuts import render, get_object_or_404
from .models import ContratoAuditado
from django.contrib.auth.decorators import login_required

def dashboard(request):
    contratos = ContratoAuditado.objects.all().order_by('-fecha_subida')
    return render(request, 'dashboard.html', {'contratos': contratos})


@login_required
def detalle_auditoria(request, pk):
    # Buscamos el contrato o devolvemos 404 si no existe
    contrato = get_object_or_404(ContratoAuditado, pk=pk)

    # Extraemos el JSON
    datos = contrato.resultado_json or {}

    return render(request, 'core/detalle.html', {
        'contrato': contrato,
        'puntos_clave': datos.get('puntos_clave', []),
        'banderas_rojas': datos.get('banderas_rojas', []),
        'riesgo': contrato.riesgo
    })