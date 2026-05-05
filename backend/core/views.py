from django.shortcuts import render, get_object_or_404, redirect
from .models import ContratoAuditado
from .forms import ContratoForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') # Al terminar, enviamos al login
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    if request.method == 'POST':
        form = ContratoForm(request.POST, request.FILES)
        if form.is_valid():
            nuevo_contrato = form.save()
            nuevo_contrato.auditar_contrato()
            return redirect('dashboard')

    # Obtenemos los contratos para listarlos
    contratos = ContratoAuditado.objects.all().order_by('-fecha_subida')
    form = ContratoForm()

    return render(request, 'core/dashboard.html', {
        'contratos': contratos,
        'form': form
    })

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