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
            model = genai.GenerativeModel('gemini-2.5-flash-lite',
                                          generation_config={"response_mime_type": "application/json"})

            # Lógica de especialización por tipo de contrato
            if isinstance(self, ContratoAlquiler):
                contexto_legal = """Eres experto en la Ley de Arrendamientos Urbanos (LAU) de España. 
                Busca: fianzas que superen el mes legal, cláusulas que impidan la prórroga legal de 5 años, 
                o intentos de cobrar honorarios de inmobiliaria al inquilino (siendo el casero empresa).
                DATOS ESPECÍFICOS DE ALQUILER:
                - Partes: Arrendador y Arrendatario.
                - Fechas: Fecha de contrato, duración y prórrogas.
                - Importes: Renta mensual, fianza (meses) y depósitos adicionales."""
            elif isinstance(self, ContratoNDA):
                contexto_legal = """Eres experto en derecho mercantil y acuerdos de confidencialidad (NDA). 
                Busca: duraciones de confidencialidad perpetuas e injustificadas, definiciones de 'Información Confidencial' 
                demasiado vagas, o penalizaciones económicas desproporcionadas.
                DATOS ESPECÍFICOS DE NDA:
                - Partes: Parte Reveladora y Parte Receptora.
                - Fechas: Fecha de efectividad y periodo de vigencia de la confidencialidad.
                - Importes: Penalizaciones por incumplimiento (cláusula penal)."""
            else:
                contexto_legal = "Eres un auditor legal experto en contratos españoles."

            prompt = f"""
                    Actúa como un experto legal en España. Analiza el texto y devuelve un JSON con esta estructura exacta:
                    {{
                        "datos_clave": {{
                            "nombres_partes": ["Nombres completos"],
                            "dni": ["DNI/NIF/CIF"],
                            "fechas": ["Fecha firma", "Fecha inicio", "Fecha fin"],
                            "importes": ["Cifras económicas detalladas (ej: Renta 800€, Fianza 1600€)"]
                        }},
                        "puntos_clave": ["Lista de 3 cláusulas principales"],
                        "banderas_rojas": ["Lista de riesgos o ilegalidades detectadas"],
                        "riesgo_total": "Bajo, Medio o Critico"
                    }}

                    CONTEXTO ADICIONAL:
                    {contexto_legal}

                    TEXTO:
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