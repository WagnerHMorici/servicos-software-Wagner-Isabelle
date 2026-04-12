import os
import shutil
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse

app = FastAPI()

PASTA_DADOS = "/dados"
HISTORICO = []

os.makedirs(PASTA_DADOS, exist_ok=True)

@app.get("/status")
def status():
    return {"status": "ok", "registros": len(HISTORICO)}

@app.post("/salvar")
async def salvar(
    file: UploadFile = File(...),
    texto: str = Form(...),
    confianca: str = Form("0.0")
):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nome_arquivo = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    caminho = os.path.join(PASTA_DADOS, nome_arquivo)

    # Salva a imagem em disco
    with open(caminho, "wb") as f:
        conteudo = await file.read()
        f.write(conteudo)

    # Registra no histórico em memória
    HISTORICO.append({
        "timestamp": timestamp,
        "arquivo": nome_arquivo,
        "texto": texto,
        "confianca": float(confianca)
    })

    return {"status": "salvo", "arquivo": nome_arquivo, "timestamp": timestamp}

@app.get("/historico")
def historico():
    return {"registros": list(reversed(HISTORICO))}  # mais recente primeiro
