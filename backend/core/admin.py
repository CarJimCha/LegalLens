from django.contrib import admin
from .models import ContratoAuditado

@admin.register(ContratoAuditado)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo', 'riesgo')
    actions = ['audit_contratos']

    @admin.action(description="Auditar contratos seleccionados")
    def audit_contratos(modeladmin, request, queryset):
        for contrato in queryset:
            contrato.auditar_contrato()