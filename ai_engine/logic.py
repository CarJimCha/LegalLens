import fitz
import re
import os
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class ContratoBase:
    def __init__(self, contenido_pdf):
        self.texto = self._extraer_texto(contenido_pdf)
        self.datos_extraidos = {"dni": [], "importes": []}

    def _extraer_texto(self, contenido):
        documento = fitz.open(stream=contenido, filetype="pdf")
        return "".join([pagina.get_text() for pagina in documento])

    def analizar(self):
        # RegEx para datos exactos
        self.datos_extraidos["dni"] = list(set(re.findall(r'\d{8}[A-Z]', self.texto)))

        # Llamada a Gemini
        analisis_ia = self._llamar_a_gemini()

        return {
            "datos_clave": self.datos_extraidos,
            "puntos_clave": analisis_ia.get("puntos_clave", []),
            "banderas_rojas": analisis_ia.get("banderas_rojas", []),
            "riesgo_total": analisis_ia.get("riesgo_total", "Bajo")
        }

    def _llamar_a_gemini(self):
        try:
            # Usamos gemini-1.5-flash (muy rápido y gratuito)
            model = genai.GenerativeModel('gemini-2.5-flash-lite',
                                          generation_config={"response_mime_type": "application/json"})

            prompt = f"""
            Eres un experto abogado auditor de contratos en España.
            Analiza el siguiente texto y devuelve un objeto JSON con:
            - "puntos_clave": lista de los 3 puntos más importantes.
            - "banderas_rojas": lista de cláusulas peligrosas o abusivas.
            - "riesgo_total": una sola palabra (Bajo, Medio o Critico).

            Texto del contrato:
            {self.texto[:8000]}
            """

            response = model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            return {"banderas_rojas": [f"Error Gemini: {str(e)}"], "riesgo_total": "Error"}


class ContratoAlquiler(ContratoBase):
    pass


class ContratoNDA(ContratoBase):
    pass