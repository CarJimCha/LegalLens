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
            nuevo_contrato = form.save(commit=False)  # No guardamos aún en DB
            nuevo_contrato.usuario = request.user  # Asignamos el dueño
            nuevo_contrato.save()
            nuevo_contrato.auditar_contrato()
            return redirect('dashboard')

    # Lógica de visibilidad
    if request.user.is_staff:
        # Los admins ven todo
        contratos = ContratoAuditado.objects.all().order_by('-fecha_subida')
    else:
        # Los usuarios normales ven solo lo suyo
        contratos = ContratoAuditado.objects.filter(usuario=request.user).order_by('-fecha_subida')

    form = ContratoForm()
    return render(request, 'core/dashboard.html', {'contratos': contratos, 'form': form})

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


@login_required
def reauditar_contrato(request, pk):
    if request.user.is_staff:
        contrato = get_object_or_404(ContratoAuditado, pk=pk)
    else:
        contrato = get_object_or_404(ContratoAuditado, pk=pk, usuario=request.user)
    contrato.auditar_contrato()
    return redirect('detalle_auditoria', pk=pk)