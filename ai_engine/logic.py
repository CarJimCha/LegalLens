import fitz
import re
import os
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class ContratoBase:
    def __init__(self, contenido_pdf):
        self.texto = self._extraer_texto(contenido_pdf)
        self.dni_regex = list(set(re.findall(r'\d{8}[A-Z]', self.texto)))

    def _extraer_texto(self, contenido):
        documento = fitz.open(stream=contenido, filetype="pdf")
        return "".join([pagina.get_text() for pagina in documento])

    def analizar(self):
        analisis_ia = self._llamar_a_gemini()
        datos_clave = analisis_ia.get("datos_clave", {})

        riesgo = analisis_ia.get("riesgo_total", "Bajo")
        if riesgo not in ["Bajo", "Medio", "Alto"]:
            riesgo = "Alto"

        return {
            "datos_clave": datos_clave,
            "puntos_clave": analisis_ia.get("puntos_clave", []),
            "banderas_rojas": analisis_ia.get("banderas_rojas", []),
            "riesgo_total": riesgo
        }

    def _llamar_a_gemini(self):
        try:
            # Usando el modelo solicitado
            model = genai.GenerativeModel('gemini-2.5-flash-lite',
                                          generation_config={"response_mime_type": "application/json"})

            prompt = f"""
            Actúa como un experto legal senior en España. Tu objetivo es auditar este contrato y detectar ILEGALIDADES.
            
            REGLA DE ORO: El campo 'riesgo_total' SOLO puede ser uno de estos tres valores: 
            'Bajo', 'Medio' o 'Alto'. 
            Prohibido usar 'Extremo', 'Crítico' o cualquier otro.

            ESTRUCTURA DE SALIDA (JSON ESTRICTO):
            {self._get_json_template()}

            INSTRUCCIONES DE AUDITORÍA ESPECÍFICA:
            {self._get_instrucciones_especificas()}

            TEXTO DEL CONTRATO:
            {self.texto[:9000]}
            """

            response = model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            return {"banderas_rojas": [f"Error crítico en IA: {str(e)}"], "riesgo_total": "Error"}


class ContratoAlquiler(ContratoBase):
    def _get_json_template(self):
        return """{
            "datos_clave": {
                "arrendador": {"nombre": "", "dni": "", "contacto": ""},
                "arrendatario": {"nombre": "", "dni": "", "contacto": ""},
                "propiedad": {"direccion": "", "metros": "", "descripcion": ""},
                "importes": {"mensualidad": "", "fianza": "", "garantia_extra": ""},
                "fechas": {"inicio": "", "duracion": ""}
            },
            "puntos_clave": [], "banderas_rojas": [], "riesgo_total": ""
        }"""

    def _get_instrucciones_especificas(self):
        return """AUDITORÍA LAU (Ley Arrendamientos Urbanos):
        1. BANDERAS ROJAS: Busca fianza > 1 mes en viviendas (Art. 36).
        2. BANDERAS ROJAS: Busca si el casero (persona jurídica) intenta cobrar honorarios de inmobiliaria al inquilino (ILEGAL según Ley Vivienda 2023).
        3. BANDERAS ROJAS: Cláusulas que impidan prórrogas hasta 5 años.
        4. BANDERAS ROJAS: Actualizaciones de renta anual > límite legal vigente (IPC/IGC).
        Si detectas alguna, descríbela citando por qué es abusiva."""


class ContratoNDA(ContratoBase):
    def _get_json_template(self):
        return """{
            "datos_clave": {
                "cliente": {"nombre": "", "dni": "", "contacto": ""},
                "proveedor": {"nombre": "", "dni": "", "contacto": ""},
                "vigencia": {"duracion": "", "periodo_post_terminacion": ""},
                "penalizaciones": {"cuantia": "", "condiciones": ""}
            },
            "puntos_clave": [], "banderas_rojas": [], "riesgo_total": ""
        }"""

    def _get_instrucciones_especificas(self):
        return """AUDITORÍA MERCANTIL (NDA):
        1. BANDERAS ROJAS: Vigencia "perpetua" o indefinida de la confidencialidad.
        2. BANDERAS ROJAS: Definición de 'Información Confidencial' que incluya información pública o de terceros.
        3. BANDERAS ROJAS: Penalizaciones desproporcionadas (ej: >100.000€ sin justificar daños).
        4. BANDERAS ROJAS: Jurisdicción fuera de España si ambas partes son españolas."""