import io
import requests
import fitz
from fastapi import FastAPI, UploadFile, File, Form
import easyocr

app = FastAPI()

print("Carregando modelos EasyOCR...")
reader_impresso = easyocr.Reader(['pt', 'en'], gpu=False)
reader_manuscrito = easyocr.Reader(['pt', 'en'], gpu=False, recog_network='handwritten')
print("Modelos prontos.")


@app.get("/status")
def status():
    return {"status": "ok", "modelos": ["impresso", "manuscrito"]}


def extrair_imagens_pdf(conteudo: bytes):
    doc = fitz.open(stream=conteudo, filetype="pdf")
    imagens = []
    for pagina in doc:
        pix = pagina.get_pixmap(dpi=200)
        imagens.append(pix.tobytes("png"))
    return imagens


@app.post("/analisar")
async def analisar_imagem(
    file: UploadFile = File(...),
    modo: str = Form("impresso")
):
    conteudo = await file.read()
    reader = reader_manuscrito if modo == "manuscrito" else reader_impresso

    if file.content_type == "application/pdf" or file.filename.endswith(".pdf"):
        imagens = extrair_imagens_pdf(conteudo)
        todos_resultados = []
        for img_bytes in imagens:
            resultados = reader.readtext(img_bytes)
            todos_resultados.extend(resultados)
    else:
        todos_resultados = reader.readtext(conteudo)

    if todos_resultados:
        texto = "\n".join([r[1] for r in todos_resultados])
        confianca = sum([r[2] for r in todos_resultados]) / len(todos_resultados)
    else:
        texto = "Nenhum texto encontrado."
        confianca = 0.0

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
        status_db = "Falha na comunicacao com armazenamento"

    return {"texto": texto, "confianca": confianca, "status_db": status_db}
