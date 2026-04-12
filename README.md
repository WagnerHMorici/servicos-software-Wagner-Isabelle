# OCR com IA Local — Projeto Final Serviços de Software 2026/1

## Funcionalidade

O usuário faz upload de uma imagem contendo texto pelo frontend Gradio.
O frontend envia o arquivo via POST REST para a api-visao, que executa OCR localmente
usando o modelo EasyOCR — sem dependência de APIs externas ou chaves de acesso.
O texto extraído é retornado ao frontend, onde pode ser baixado como .txt,
e também salvo pela api-armazenamento, que persiste a imagem em disco e mantém
um histórico consultável pela interface.

## Arquitetura

```
[Usuário]
    |
[gradio-visao :7861]
    |
    |-- POST /analisar (imagem + modo) --> [api-visao :8081]
    |                                            |
    |                                      EasyOCR (local)
    |                                            |
    |                                   POST /salvar
    |                                            |
    |                                   [api-armazenamento :8082]
    |                                    (persiste em /dados)
    |
    |-- GET /historico --> [api-armazenamento :8082]
```

## Estrutura

```
projeto/
├── compose.yaml
├── README.md
├── gradio-visao/               # Frontend (Gradio)
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── api-visao/                  # Backend OCR (EasyOCR + FastAPI)
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
└── api-armazenamento/          # Backend de persistência (FastAPI)
    ├── main.py
    ├── requirements.txt
    └── Dockerfile
```

## Funcionalidades

- Upload de imagens (PNG, JPG) pela interface
- Dois modos de reconhecimento: texto impresso e texto manuscrito
- Barra de progresso durante o processamento
- Preview da imagem processada ao lado do resultado
- Percentual de confiança da predição exibido na interface
- Download do texto extraído em formato .txt
- Histórico de análises realizadas consultável pela interface
- Imagens persistidas em volume Docker entre reinicializações

## Como rodar

```bash
docker compose up --build
```

Acesse: http://localhost:7861

## Observações

- Os modelos EasyOCR são baixados automaticamente na primeira execução (~400MB).
- Funciona 100% offline após o primeiro build.
- O histórico fica em memória durante a sessão; as imagens são persistidas no volume Docker dados-imagens.

## Descrição para entrega

O usuário faz upload de uma imagem pelo frontend Gradio, escolhendo entre modo
impresso ou manuscrito. O frontend envia o arquivo via REST para a api-visao,
que executa OCR localmente com EasyOCR (suporte a português e inglês), retornando
o texto extraído e a confiança da predição. O resultado é salvo pela api-armazenamento,
que persiste o arquivo em disco e mantém histórico consultável pela interface.
O texto extraído pode ser baixado como .txt diretamente pela interface.
