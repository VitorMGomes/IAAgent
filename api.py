from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os, json
from functions.tools import tools
from functions.dispatcher import call_function
import pandas as pd

# Configurações iniciais
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
df = pd.read_csv("data/Dados.csv")
cabecalho = df.columns.tolist()

# Prompt fixo
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

# Inicializa o app FastAPI
app = FastAPI()

# Novo modelo para aceitar histórico completo
class Historico(BaseModel):
    messages: list[dict]

@app.post("/pergunta")
def responder_pergunta(p: Historico):
    try:
        messages = p.messages

        # Adiciona o system prompt se ainda não estiver no histórico
        if not any(m["role"] == "system" for m in messages):
            messages.insert(0, {"role": "system", "content": system_prompt})

        completion = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=messages,
            tools=tools
        )

        assistant_message = completion.choices[0].message
        messages.append(assistant_message)

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

            messages.append({
                "role": "user",
                "content": "Responda de forma clara e direta. Evite explicações extras se a pergunta for objetiva."
            })

            class RespostaFinalMelhorada(BaseModel):
                response: str

            final = client.beta.chat.completions.parse(
                model="gpt-4.1-mini-2025-04-14",
                messages=messages,
                response_format=RespostaFinalMelhorada
            )

            return {"resposta": final.choices[0].message.parsed.response}

        else:
            return {"resposta": assistant_message.content}

    except Exception as e:
        print("Erro interno na API:", e)
        raise HTTPException(status_code=500, detail=str(e))
