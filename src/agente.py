import json
import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI
import numpy as np

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from functions.tools import tools            # lista de definições de funções para o modelo
from functions.dispatcher import call_function

# ------------------------------------------------------------
# Função auxiliar que plota um insight retornado pelas funções
# ------------------------------------------------------------

def convert_numpy_types(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    return str(obj)


def plot_insight(insight: dict):
    """Renderiza um insight no Matplotlib (linha, barra ou pizza)."""
    tipo   = insight["tipo"]
    titulo = insight["titulo"]
    eixo_x = insight["eixo_x"]
    eixo_y = insight["eixo_y"]
    dados  = insight["dados"]

    plt.figure(figsize=(8, 4))
    if tipo == "linha":
        plt.plot(eixo_x, dados, marker="o")
        plt.ylabel(eixo_y)
    elif tipo == "barra":
        plt.bar(eixo_x, dados)
        plt.ylabel(eixo_y)
    elif tipo == "pizza":
        labels = [item["label"] for item in dados]
        vals   = [item["value"] for item in dados]
        plt.pie(vals, labels=labels, autopct="%1.1f%%")
    plt.title(titulo)
    if tipo != "pizza":
        plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# ------------------------------------------------------------
# Carrega variáveis de ambiente e inicializa OpenAI
# ------------------------------------------------------------

env_file = os.getenv("ENV_FILE", ".env")
load_dotenv(env_file)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------------------------------------------
# Lê o CSV para extrair header (usado no system prompt)
# ------------------------------------------------------------

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(base_dir, "src", "data", "Dados.csv")


df = pd.read_csv(csv_path)
cabecalho = df.columns.tolist()

# ------------------------------------------------------------
# (Opcional) RAG via Chroma se você quiser usar na conversa
# ------------------------------------------------------------

retriever = Chroma(
    persist_directory="./.chrome_langchain_db",
    embedding_function=OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY")),
).as_retriever()

# ------------------------------------------------------------
# Prompt de sistema
# ------------------------------------------------------------

system_prompt = f"""
Você é um agente inteligente que responde dúvidas sobre a folha de pagamento de um colaborador individual.
Nunca fale sobre dados de outros colaboradores ou sobre valores médios da empresa.
Sempre responda com base apenas nos dados do colaborador atual.

Essas são as colunas disponíveis na folha de pagamento: {', '.join(cabecalho)}.
Ao usar funções que exigem o nome de uma coluna, use **exatamente** os nomes listados acima. Não traduza nem reescreva os nomes das colunas.

Você pode consultar documentos PDF e textos técnicos (como explicações sobre FGTS, PIS, IRRF, CBO etc.) que foram carregados na base vetorial.
Se os documentos não forem suficientes, você pode complementar a resposta com seu conhecimento prévio confiável sobre leis trabalhistas, benefícios e temas relacionados à folha de pagamento no Brasil.
Evite mencionar valores fixos de impostos, percentuais ou faixas salariais que possam ter mudado, a menos que estejam presentes nos documentos carregados.

**Instruções de resposta:**
- Se a resposta for valores em moeda, **responda em reais ou na notação da moeda**
- Se a pergunta do usuário for conceitual (como “o que é FGTS?”), **responda de forma completa e clara**, usando os documentos e seu conhecimento se necessário.
"""

# ------------------------------------------------------------
# Loop de conversa
# ------------------------------------------------------------

messages = [{"role": "system", "content": system_prompt}]

while True:
    user_question = input("\nDigite sua pergunta sobre a folha de pagamento (ou 'sair' para encerrar): ")
    if user_question.strip().lower() in {"sair", "exit", "quit"}:
        print("\nEncerrando o assistente.")
        break

    # registra pergunta
    messages.append({"role": "user", "content": user_question})

    # primeira chamada ao modelo (pode retornar function_call)
    completion = client.chat.completions.create(
        model="gpt-4.1-mini-2025-04-14",
        messages=messages,
        tools=tools,
    )

    assistant_message = completion.choices[0].message
    messages.append(assistant_message)

    print(f"\nTokens usados nesta etapa: {completion.usage.total_tokens} tokens")

    # --------------------------------------------------------
    # Se o modelo quis chamar alguma função, executa
    # --------------------------------------------------------
    if assistant_message.tool_calls:
        for call in assistant_message.tool_calls:
            nome = call.function.name
            try:
                argumentos = json.loads(call.function.arguments)
            except json.JSONDecodeError:
                argumentos = {}

            # executa função real
            try:
                resultado = call_function(nome, argumentos)
            except Exception as e:
                resultado = {"erro": str(e)}
                
            print(f"\n🚀 Chamando função: {nome}({json.dumps(argumentos, default=str, ensure_ascii=False)})")

            # envia resultado de volta ao LLM (role=tool)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(resultado, default=str)
            })

            # imprime resultado para o terminal
            print("\n🔧 Resultado da função:")
            print(json.dumps(resultado, indent=2, ensure_ascii=False, default=convert_numpy_types))

            # ---- NOVO: plota qualquer insight retornado ----
            if isinstance(resultado, dict) and "insights" in resultado:
                for ins in resultado["insights"]:
                    plot_insight(ins)

        # segunda chamada ao modelo para gerar resposta final
        final = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=messages,
        )
        resposta_final = final.choices[0].message.content
        messages.append({"role": "assistant", "content": resposta_final})
        print("\n💬 Resposta final do agente:\n", resposta_final)

    # --------------------------------------------------------
    # Caso não tenha function_call (resposta direta)
    # --------------------------------------------------------
    else:
        print("\n💬 Resposta final do agente:\n", assistant_message.content)
