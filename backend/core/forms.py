from django import forms
from .models import ContratoAuditado

class ContratoForm(forms.ModelForm):
    class Meta:
        model = ContratoAuditado
        fields = ['cliente', 'tipo', 'archivo']
        widgets = {
            'cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
        }