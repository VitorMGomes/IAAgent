# 🤖 Slip Pay-Agent

Um agente de inteligência artificial desenvolvido em Python que responde dúvidas sobre a **folha de pagamento de colaboradores** de forma personalizada e visual. O sistema une **FastAPI**, **Streamlit** e **OpenAI** para oferecer uma experiência interativa com **gráficos automatizados**, **respostas inteligentes** e **visualização de dados salariais**.

---

## ⚙️ Funcionalidades

- 🔍 Responde perguntas sobre valores e conceitos da folha de pagamento
- 📊 Geração automática de gráficos com base nas perguntas
- 💬 Interface de conversa com IA (usando OpenAI + function calling)
- 📁 Recuperação de documentos explicativos via RAG (ChromaDB)
- 🔐 Acesso individualizado por colaborador (apenas seus próprios dados)
- 🧠 Suporte a perguntas técnicas com base em documentos indexados (ex: FGTS, IRRF)
- 🧾 Processamento da folha de pagamento em CSV

---

## 🚀 Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/seuusuario/slip-pay-agent.git
cd slip-pay-agent
```
### 2. Crie e ative um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure variáveis de ambiente

Crie um arquivo .env baseado no .env.example, e adicione sua chave da OpenAI:

```bash
OPENAI_API_KEY=sk-xxxx...
```

### 5. Execute o sistema completo
```bash
python src/main.py
```

## 📂 Estrutura do Projeto

```bash
    IAAgent/
├── src/
│ ├── api.py # API FastAPI com os endpoints
│ ├── agente.py # Agente inteligente (não utilizado no projeto final)
│ ├── main.py # Executa API e UI em paralelo
│
│ ├── data/
│ │ └── Dados.csv # Arquivo principal da folha de pagamento
│
│ ├── documentos/ # Base de documentos para RAG
│
│ ├── functions/
│ │ ├── dispatcher.py # Função que despacha chamadas das tools
│ │ ├── folha_tools.py # Funções especializadas em folha de pagamento
│ │ └── tools.py # Funções genéricas do agente
│
│ ├── ingest/
│ │ └── pdf_ingestor.py # Indexador de documentos PDF para RAG
│
│ ├── ui/
│ │ ├── Home.py # Página inicial com visualização geral
│ │ └── pages/ # Subpáginas de navegação Streamlit
│ │ ├── 1_Visualizacao_Personalizada.py
│ │ ├── 2_Insights_Personalizados.py
│ │ └── 3_ChatBot.py
│
├── .env # Variáveis de ambiente (chave da OpenAI etc.)
├── .env.example # Exemplo do arquivo .env
├── requirements.txt # Dependências do projeto
├── README.md # Documentação do projeto
├── .gitignore # Arquivos e pastas ignoradas pelo Git
└── venv/ # Ambiente virtual Python (não versionado)
```