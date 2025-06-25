# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal, List, Dict, Optional
import os, json, pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

from functions.tools import tools       # seu dispatcher de ferramentas
from functions.dispatcher import call_function

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
df = pd.read_csv("data/Dados.csv")
cabecalho = df.columns.tolist()

system_prompt = f"""
Você é um agente inteligente que responde dúvidas sobre a folha de pagamento de um colaborador individual.
Nunca fale sobre dados de outros colaboradores ou sobre valores médios da empresa.
Sempre responda com base apenas nos dados do colaborador atual.

Colunas disponíveis: {', '.join(cabecalho)}.
Use **exatamente** esses nomes ao chamar funções.

Não mencione gráficos ou visualizações. Apenas responda objetivamente.
"""

mensagens: List[Dict] = [{"role": "system", "content": system_prompt}]

class Pergunta(BaseModel):
    user_message: str

class Insight(BaseModel):
    tipo: Literal["texto","grafico_barras","grafico_linha","grafico_pizza"]
    titulo: str
    conteudo: Optional[str] = None
    dados:     Optional[List[Dict[str,float]]] = None
    eixo_x:    Optional[str] = None
    eixo_y:    Optional[str] = None
    valor_total: Optional[float] = None

app = FastAPI()

@app.post("/pergunta")
def pergunta(p: Pergunta):
    try:
        mensagens.append({"role":"user","content":p.user_message})
        # 1ª rodada: LLM + ferramentas
        comp = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=mensagens,
            tools=tools
        )
        asm = comp.choices[0].message
        mensagens.append(asm)

        if not asm.tool_calls:
            # sem ferramenta → só retorna texto
            return {"resposta": asm.content, "insight": None}

        # executa tool calls
        for tc in asm.tool_calls:
            res = call_function(tc.function.name, json.loads(tc.function.arguments))
            mensagens.append({
                "role":"tool",
                "tool_call_id": tc.id,
                "content": json.dumps(res, default=str)
            })

        # 2ª rodada: resposta clara
        mensagens.append({
            "role":"user",
            "content":"Responda de forma clara e direta. Não mencione gráficos."
        })
        final = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=mensagens
        )
        resposta = final.choices[0].message.content
        mensagens.append({"role":"assistant","content":resposta})

        # 3ª rodada: gere o insight JSON STANDALONE
        try:
            mensagens.append({
                "role":"user",
                "content":"Agora gere apenas um objeto JSON para visualização, com tipo, título, eixos e dados."
            })
            comp_ins = client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=mensagens,
                response_format=Insight
            )
            insight = comp_ins.choices[0].message.parsed
        except Exception:
            insight = None

        return {"resposta": resposta, "insight": insight}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
