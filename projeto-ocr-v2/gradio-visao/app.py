import gradio as gr
import requests

def analisar_imagem(imagem_path):
    if imagem_path is None:
        return None, "Nenhuma imagem enviada.", ""

    with open(imagem_path, "rb") as f:
        files = {"file": f}
        try:
            response = requests.post("http://api-visao:8081/analisar", files=files)
            if response.status_code == 200:
                dados = response.json()
                texto = dados.get("texto", "")
                confianca = dados.get("confianca", 0) * 100
                status_db = dados.get("status_db", "")
                info = f"Confiança: {confianca:.1f}%\nStatus: {status_db}"
                return imagem_path, texto, info
            else:
                return imagem_path, f"Erro no servidor: {response.status_code}", ""
        except Exception as e:
            return imagem_path, f"Erro de comunicação: {str(e)}", ""

def buscar_historico():
    try:
        response = requests.get("http://api-armazenamento:8082/historico")
        if response.status_code == 200:
            registros = response.json().get("registros", [])
            if not registros:
                return "Nenhum registro encontrado."
            linhas = []
            for r in registros:
                linhas.append(f"{r['timestamp']} | {r['arquivo']} | {r['texto'][:80]}...")
            return "\n".join(linhas)
        return "Erro ao buscar histórico."
    except Exception as e:
        return f"Erro: {str(e)}"

with gr.Blocks(title="OCR com IA Local") as demo:
    gr.Markdown("#OCR com IA Local\nEnvie uma imagem com texto impresso e a IA extrai o conteúdo — 100% local, sem API externa.")

    with gr.Row():
        with gr.Column():
            entrada = gr.Image(type="filepath", label="Imagem de entrada")
            botao = gr.Button("Extrair Texto", variant="primary")
        with gr.Column():
            preview = gr.Image(label="Preview da imagem processada")
            texto_saida = gr.Textbox(label="Texto extraído", lines=6)
            info_saida = gr.Textbox(label="Informações (confiança / status)", lines=2)

    botao.click(fn=analisar_imagem, inputs=entrada, outputs=[preview, texto_saida, info_saida])

    gr.Markdown("---")
    gr.Markdown("## 🗂️ Histórico de análises")
    with gr.Row():
        botao_historico = gr.Button("Atualizar histórico")
        historico_saida = gr.Textbox(label="Últimas análises", lines=8)
    botao_historico.click(fn=buscar_historico, inputs=[], outputs=historico_saida)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7861)
