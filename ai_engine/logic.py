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
                o intentos de cobrar honorarios de inmobiliaria al inquilino (siendo el casero empresa)."""
            elif isinstance(self, ContratoNDA):
                contexto_legal = """Eres experto en derecho mercantil y acuerdos de confidencialidad (NDA). 
                Busca: duraciones de confidencialidad perpetuas e injustificadas, definiciones de 'Información Confidencial' 
                demasiado vagas, o penalizaciones económicas desproporcionadas."""
            else:
                contexto_legal = "Eres un auditor legal experto en contratos españoles."

            prompt = f"""
            {contexto_legal}
            Analiza el texto y extrae la información requerida en este formato JSON exacto:
            {{
                "datos_clave": {{
                    "nombres_partes": ["Nombre completo o empresa de cada firmante"],
                    "dni": ["DNI o CIF de cada parte"],
                    "fechas": ["Fecha de firma, inicio y fin si existen"],
                    "importes": ["Renta, fianza, penalizaciones o cuantías mencionadas"]
                }},
                "puntos_clave": ["Lista de 3 puntos fundamentales del acuerdo"],
                "banderas_rojas": ["Lista de cláusulas ilegales, abusivas o de alto riesgo"],
                "riesgo_total": "Bajo, Medio o Critico"
            }}

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