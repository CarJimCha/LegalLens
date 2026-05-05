import requests  # Asegúrate de que 'requests' esté en el requirements.txt del backend
from django.db import models
from django.conf import settings

class ContratoAuditado(models.Model):
    tipo_contrato = [
        ('alquiler', 'Alquiler'),
        ('nda', 'NDA'),
    ]

    cliente = models.CharField(max_length=200)
    archivo = models.FileField(upload_to='contratos/')
    tipo = models.CharField(max_length=20, choices=tipo_contrato)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contratos',
        null=True,  # Lo dejamos null temporalmente para la migración
        blank=True
    )

    # Aquí guardaremos el JSON que nos devuelva FastAPI
    resultado_json = models.JSONField(null=True, blank=True)
    riesgo = models.CharField(max_length=20, default="Pendiente")

    def auditar_contrato(self):
        """Envía el PDF al servicio de IA y guarda el resultado real"""
        import json
        try:
            with self.archivo.open('rb') as f:
                archivos = {'archivo': (self.archivo.name, f, 'application/pdf')}
                # IMPORTANTE: Usa self.tipo (que es el campo del modelo)
                datos = {'tipo': self.tipo}

                respuesta = requests.post(
                    "http://ai-engine:8000/analizar",
                    files=archivos,
                    data=datos,
                    timeout=30
                )

            if respuesta.status_code == 200:
                resultado = respuesta.json()

                # 1. Guardamos todo el objeto en el JSONField
                self.resultado_json = resultado

                # 2. Mapeamos "riesgo_total" de la IA al campo "riesgo" del modelo
                # Usamos .get() por seguridad si la IA falla en la clave
                self.riesgo = resultado.get("riesgo_total", "Bajo")

                # 3. Guardamos los cambios en la DB
                self.save()
            else:
                self.riesgo = "Error"
                self.save()

        except Exception as e:
            print(f"Error en auditoría: {e}")
            self.riesgo = "Error"
            self.save()


    def __str__(self):
        return f"{self.cliente} - {self.tipo}"