import json
import os
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from functions.tools import tools
from functions.dispatcher import call_function
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import pandas as pd

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
df = pd.read_csv("data/Dados.csv")

retriever = Chroma(
    persist_directory="./.chrome_langchain_db",
    embedding_function=OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
).as_retriever()

cabecalho = df.columns.tolist()
prompt_colunas = f"Essas são as colunas disponíveis na folha de pagamento: {', '.join(cabecalho)}."

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
- Se a pergunta do usuário for sobre um valor (como salário, comissão, desconto, FGTS, etc.), **responda apenas com o número e o mês/ano correspondente**. Não adicione explicações extras.
- Se a pergunta do usuário for conceitual (como “o que é FGTS?” ou “como funciona o IRRF?”), **responda de forma completa, clara e explicativa**, utilizando os documentos e seu conhecimento se necessário.
"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Qual o total de horas extras de janeiro de 2021 a dezembro 2022? E qual o maior salario base do colaborador em seu tempo de empresa?"}
]

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
)

assistant_message = completion.choices[0].message
messages.append(assistant_message)

# Se houver chamadas de função, processa
if assistant_message.tool_calls:
    for tool_call in assistant_message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        result = call_function(name, args)

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result, default=str)
        })

    # Mensagem de revisão final após uso de ferramentas
    messages.append({
        "role": "user",
        "content": (
            "Responda de forma clara e direta. Evite explicações extras se a pergunta for objetiva."
        )
    })

    class RespostaFinalMelhorada(BaseModel):
        response: str = Field(description="Uma resposta clara e direta com os resultados solicitados.")

    completion_2 = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=messages,
        response_format=RespostaFinalMelhorada
    )

    final_response = completion_2.choices[0].message.parsed
    print("Resposta final do agente:\n", final_response.response)

else:
    # Caso não haja tool_call, imprime a resposta direta do modelo
    print("Resposta final do agente:\n", assistant_message.content)
