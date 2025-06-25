import json
import os
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
from functions.tools import tools
from functions.dispatcher import call_function
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import pandas as pd
from typing import Literal, List, Dict

# Carrega variáveis de ambiente (.env)
load_dotenv()

# Inicializa cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Carrega dados da folha de pagamento
df = pd.read_csv("data/Dados.csv")

# Inicializa a base vetorial com Chroma + embeddings
retriever = Chroma(
    persist_directory="./.chrome_langchain_db",
    embedding_function=OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY")),
).as_retriever()

# Define colunas disponíveis no CSV
cabecalho = df.columns.tolist()

# System prompt: instruções fixas para o agente
system_prompt = f"""
Você é um agente inteligente que responde dúvidas sobre a folha de pagamento de um colaborador individual.
Nunca fale sobre dados de outros colaboradores ou sobre valores médios da empresa.
Sempre responda com base apenas nos dados do colaborador atual.

Essas são as colunas disponíveis na folha de pagamento: {', '.join(cabecalho)}.
Ao usar funções que exigem o nome de uma coluna, use **exatamente** os nomes listados acima. Não traduza nem reescreva os nomes das colunas.

Você pode consultar documentos PDF e textos técnicos (como explicações sobre FGTS, PIS, IRRF, CBO etc) que foram carregados na base vetorial.
Se os documentos não forem suficientes, você pode complementar a resposta com seu conhecimento prévio confiável sobre leis trabalhistas, benefícios e temas relacionados à folha de pagamento no Brasil.
Evite mencionar valores fixos de impostos, percentuais ou faixas salariais que possam ter mudado, a menos que estejam presentes nos documentos carregados.

**Instruções de resposta:**
- Se a resposta for valores em moeda, **responda em reais ou na notação da moeda**
- Se a pergunta do usuário for conceitual (como “o que é FGTS?” ou “como funciona o IRRF?”), **responda de forma completa, clara e explicativa**, utilizando os documentos e seu conhecimento se necessário.
"""

# Modelo unificado para insights
class Insight(BaseModel):
    tipo: Literal["texto", "grafico_barras", "grafico_linha", "grafico_pizza"]
    titulo: str
    conteudo: str | None = None
    dados: List[Dict[str, float]] | None = None
    eixo_x: str | None = None
    eixo_y: str | None = None
    valor_total: float | None = None

# Lista de mensagens com o system prompt inicial
messages = [{"role": "system", "content": system_prompt}]
insights_acumulados = []

# Início do loop de conversa
while True:
    user_question = input("\nDigite sua pergunta sobre a folha de pagamento (ou 'sair' para encerrar): ")
    if user_question.strip().lower() in {"sair", "exit", "quit"}:
        print("Encerrando o assistente.")
        break

    messages.append({"role": "user", "content": user_question})

    completion = client.chat.completions.create(
        model="gpt-4.1-mini-2025-04-14",
        messages=messages,
        tools=tools,
    )

    assistant_message = completion.choices[0].message
    messages.append(assistant_message)

    print(f"\nTokens usados nesta etapa: {completion.usage.total_tokens} tokens")

    if assistant_message.tool_calls:
        for tool_call in assistant_message.tool_calls:
            name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                args = {}

            print(f"\nFunção chamada: {name}")
            print("Argumentos:", args)

            try:
                result = call_function(name, args)
            except Exception as e:
                result = {"erro": str(e)}

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, default=str)
            })

        messages.append({
            "role": "user",
            "content": "Responda de forma clara e direta. Evite explicações extras se a pergunta for objetiva."
        })

        # Geração paralela do insight estruturado
        try:
            completion_2 = client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=messages,
                response_format=Insight
            )
            insight = completion_2.choices[0].message.parsed
            insights_acumulados.append(insight)

            print("\n📊 Insight estruturado gerado com sucesso!")
            print(f"Tipo: {insight.tipo} | Título: {insight.titulo}")

        except Exception as e:
            print("⚠️ Falha ao gerar insight estruturado:", e)

        # Geração da resposta textual para o chat
        final_response = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=messages,
        )
        resposta_final = final_response.choices[0].message.content
        messages.append({"role": "assistant", "content": resposta_final})
        print("\n💬 Resposta final do agente:\n", resposta_final)

    else:
        print("\n💬 Resposta final do agente:\n", assistant_message.content)
