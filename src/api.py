from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, json, io, base64
import pandas as pd
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from typing import List, Any, Dict

from openai import OpenAI
from functions.tools import tools
from functions.dispatcher import call_function

# ------------------------------------------------------------------
# Configuração inicial
# ------------------------------------------------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

df = pd.read_csv("data/Dados.csv")
cabecalho = df.columns.tolist()

app = FastAPI()


# ------------------------------------------------------------------
# Utilitário para converter valores NumPy → tipos nativos
# ------------------------------------------------------------------
def convert_numpy_types(obj: Any):
    import numpy as np
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    return str(obj)


def safe_response(data: Dict):
    """Garante que o payload só contenha tipos JSON‐serializáveis."""
    return json.loads(json.dumps(data, default=convert_numpy_types))


# ------------------------------------------------------------------
# Modelos Pydantic
# ------------------------------------------------------------------
class Pergunta(BaseModel):
    mensagem: str


class Chamada(BaseModel):
    nome: str
    argumentos: dict


# ------------------------------------------------------------------
# Armazena contexto do chat em memória (simplificado)
# ------------------------------------------------------------------
chat_history: List[Dict] = []


# ------------------------------------------------------------------
# ENDPOINT /chat
# ------------------------------------------------------------------
@app.post("/chat")
def conversar(pergunta: Pergunta):
    global chat_history

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

    if not chat_history:
        chat_history.append({"role": "system", "content": system_prompt})

    chat_history.append({"role": "user", "content": pergunta.mensagem})

    resp = client.chat.completions.create(
        model="gpt-4.1-mini-2025-04-14",
        messages=chat_history,
        tools=tools,
    )
    assistant_msg = resp.choices[0].message
    chat_history.append(assistant_msg)

    # ------------------------------------------------------------ #
    # Se o LLM chamou funções                                        #
    # ------------------------------------------------------------ #
    if assistant_msg.tool_calls:
        insights_coletados = []

        for tc in assistant_msg.tool_calls:
            nome = tc.function.name
            try:
                args = json.loads(tc.function.arguments)
                resultado = call_function(nome, args)
            except Exception as e:
                resultado = {"erro": str(e)}

            chat_history.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(resultado, default=convert_numpy_types)
            })

            insights_coletados.append(resultado)

        # Gera resposta final após a execução das funções
        final_resp = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=chat_history
        )
        final_text = final_resp.choices[0].message.content
        chat_history.append({"role": "assistant", "content": final_text})

        return safe_response({"resposta": final_text, "insights": insights_coletados})

    # ------------------------------------------------------------ #
    # Caso não haja function_call                                    #
    # ------------------------------------------------------------ #
    return safe_response({"resposta": assistant_msg.content})


# ------------------------------------------------------------------
# ENDPOINT /chamar – executa função diretamente
# ------------------------------------------------------------------
@app.post("/chamar")
def chamar_funcao(req: Chamada):
    try:
        resultado = call_function(req.nome, req.argumentos)
        return safe_response(resultado)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ------------------------------------------------------------------
# ENDPOINT /grafico – gera imagens base64 a partir dos insights
# ------------------------------------------------------------------
@app.post("/grafico")
def gerar_grafico(req: Chamada):
    try:
        insight_dict = call_function(req.nome, req.argumentos)
        if "insights" not in insight_dict:
            raise ValueError("Nenhum insight retornado.")

        imagens = []
        for ins in insight_dict["insights"]:
            plt.figure(figsize=(8, 4))
            tipo = ins["tipo"]
            if tipo == "linha":
                plt.plot(ins["eixo_x"], ins["dados"], marker="o")
                plt.ylabel(ins["eixo_y"])
            elif tipo == "barra":
                plt.bar(ins["eixo_x"], ins["dados"])
                plt.ylabel(ins["eixo_y"])
            elif tipo == "pizza":
                labels = [d["label"] for d in ins["dados"]]
                vals = [d["value"] for d in ins["dados"]]
                plt.pie(vals, labels=labels, autopct="%1.1f%%")
            plt.title(ins["titulo"])
            if tipo != "pizza":
                plt.xticks(rotation=45)
            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            plt.close()
            imagens.append(base64.b64encode(buf.getvalue()).decode())

        payload = {"insights": insight_dict["insights"], "imagens_base64": imagens}
        return safe_response(payload)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ------------------------------------------------------------------
# ENDPOINT /dados – devolve o holerite completo
# ------------------------------------------------------------------
@app.get("/dados")
def get_dados():
    registros = df.to_dict(orient="records")
    return safe_response(registros)
