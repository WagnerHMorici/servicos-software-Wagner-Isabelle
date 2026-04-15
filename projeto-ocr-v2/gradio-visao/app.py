import gradio as gr
import requests
import tempfile
import os


def analisar_imagem(arquivo_path, modo, progresso=gr.Progress()):
    if arquivo_path is None:
        return None, "Nenhum arquivo enviado.", ""

    progresso(0.1, desc="Lendo arquivo...")
    nome_arquivo = os.path.basename(arquivo_path)
    content_type = "application/pdf" if arquivo_path.endswith(".pdf") else "image/png"

    progresso(0.3, desc="Enviando para o backend...")
    with open(arquivo_path, "rb") as f:
        files = {"file": (nome_arquivo, f, content_type)}
        data = {"modo": modo}
        try:
            progresso(0.5, desc="Processando com IA...")
            response = requests.post(
                "http://api-visao:8081/analisar",
                files=files,
                data=data
            )
            progresso(0.9, desc="Finalizando...")
            if response.status_code == 200:
                dados = response.json()
                texto = dados.get("texto", "")
                confianca = dados.get("confianca", 0) * 100
                status_db = dados.get("status_db", "")
                info = f"Confianca: {confianca:.1f}%\nStatus: {status_db}"
                preview = arquivo_path if not arquivo_path.endswith(".pdf") else None
                progresso(1.0, desc="Concluido.")
                return preview, texto, info
            else:
                return None, f"Erro no servidor: {response.status_code}", ""
        except Exception as e:
            return None, f"Erro de comunicacao: {str(e)}", ""


def baixar_texto(texto):
    if not texto or texto.strip() == "":
        return None
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    tmp.write(texto)
    tmp.close()
    return tmp.name


def buscar_historico():
    try:
        response = requests.get("http://api-armazenamento:8082/historico")
        if response.status_code == 200:
            registros = response.json().get("registros", [])
            if not registros:
                return "Nenhum registro encontrado."
            linhas = []
            for r in registros:
                linhas.append(
                    f"{r['timestamp']}  |  {r['arquivo']}  |  {r['texto'][:80]}..."
                )
            return "\n".join(linhas)
        return "Erro ao buscar historico."
    except Exception as e:
        return f"Erro: {str(e)}"


with gr.Blocks(title="OCR com IA Local") as demo:
    gr.Markdown("# OCR com IA Local")
    gr.Markdown("Envie uma imagem ou PDF com texto e a IA extrai o conteudo - 100% local, sem API externa.")

    with gr.Row():
        with gr.Column():
            entrada = gr.File(
                label="Arquivo de entrada (imagem ou PDF)",
                file_types=["image", ".pdf"]
            )
            modo = gr.Radio(
                choices=["impresso", "manuscrito"],
                value="impresso",
                label="Modo de reconhecimento"
            )
            botao = gr.Button("Extrair Texto", variant="primary")

        with gr.Column():
            preview = gr.Image(label="Preview da imagem processada")
            texto_saida = gr.Textbox(label="Texto extraido", lines=8)
            info_saida = gr.Textbox(label="Confianca e status", lines=2)
            botao_download = gr.Button("Baixar texto como .txt")
            arquivo_download = gr.File(label="Arquivo para download")

    botao.click(
        fn=analisar_imagem,
        inputs=[entrada, modo],
        outputs=[preview, texto_saida, info_saida]
    )

    botao_download.click(
        fn=baixar_texto,
        inputs=[texto_saida],
        outputs=[arquivo_download]
    )

    gr.Markdown("---")
    gr.Markdown("## Historico de analises")
    with gr.Row():
        botao_historico = gr.Button("Atualizar historico")
        historico_saida = gr.Textbox(label="Ultimas analises", lines=8)
    botao_historico.click(fn=buscar_historico, inputs=[], outputs=historico_saida)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7861)
