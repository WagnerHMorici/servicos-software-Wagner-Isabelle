import io
import requests
from fastapi import FastAPI, UploadFile, File
import easyocr

app = FastAPI()

print("Carregando modelo EasyOCR local...")
reader = easyocr.Reader(['pt', 'en'], gpu=False)
print("Modelo pronto.")

@app.get("/status")
def status():
    return {"status": "ok", "modelo": "easyocr-pt-en"}

@app.post("/analisar")
async def analisar_imagem(file: UploadFile = File(...)):
    conteudo = await file.read()

    resultados = reader.readtext(conteudo)

    if resultados:
        texto = "\n".join([r[1] for r in resultados])
        confianca = sum([r[2] for r in resultados]) / len(resultados)
    else:
        texto = "Nenhum texto encontrado na imagem."
        confianca = 0.0

    # Envia para armazenamento
    files_req = {"file": (file.filename, conteudo, file.content_type)}
    data = {"texto": texto, "confianca": str(confianca)}
    try:
        res_db = requests.post(
            "http://api-armazenamento:8082/salvar",
            files=files_req,
            data=data
        )
        status_db = "Salvo com sucesso" if res_db.status_code == 200 else "Erro ao salvar"
    except Exception:
        status_db = "Falha na comunicação com armazenamento"

    return {"texto": texto, "confianca": confianca, "status_db": status_db}
