from fastapi import FastAPI, UploadFile, File, Form
# Importamos las clases que creamos en logic.py
from logic import ContratoAlquiler, ContratoNDA

# Todas sus rutas internas deben tener el prefijo /api para que Nginx las encuentre
app = FastAPI(root_path="/api")


@app.get("/")
def read_root():
    return {"message": "LegalLens AI Engine está vivo"}


@app.post("/analizar")
async def analizar_contrato(tipo: str = Form(...), archivo: UploadFile = File(...)):
    contenido = await archivo.read()

    if tipo == "alquiler":
        contrato = ContratoAlquiler(contenido)
    elif tipo == "nda":
        contrato = ContratoNDA(contenido)
    else:
        return {"error": "Tipo no soportado"}

    # Fíjate que ahora no pasamos 'cliente_ia' porque lo quitamos de logic.py[cite: 1]
    resultado = contrato.analizar()
    return resultado